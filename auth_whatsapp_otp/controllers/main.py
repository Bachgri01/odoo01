# -*- coding: utf-8 -*-
import logging
import random
import string
from datetime import datetime, timedelta

from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)

from odoo.addons.web.controllers.home import Home

class WhatsAppOTPLogin(Home):

    def _send_whatsapp_message(self, mobile, message):
        """Helper to send WhatsApp message via UltraMsg"""
        ICP = request.env['ir.config_parameter'].sudo()
        instance_id = ICP.get_param('auth_whatsapp_otp.ultramsg_instance_id')
        token = ICP.get_param('auth_whatsapp_otp.ultramsg_token')

        if not instance_id or not token:
            _logger.error("UltraMsg Instance ID or Token not configured.")
            return False

        import requests
        url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
        payload = {
            "token": token,
            "to": mobile,
            "body": message,
            "priority": 10,
            "referenceId": ""
        }
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        
        try:
            response = requests.post(url, data=payload, headers=headers)
            res_data = response.json()
            if res_data.get('sent') == 'true' or res_data.get('success'):
                return True
            _logger.error(f"UltraMsg Error: {res_data}")
            return False
        except Exception as e:
            _logger.error(f"WhatsApp Sending Error: {str(e)}")
            return False

    @http.route('/web/login/whatsapp/send_otp', type='json', auth="none", methods=['POST'])
    def send_otp(self, mobile):
        if not mobile:
            return {'error': _('Please enter your WhatsApp number.')}

        # Find user by mobile number
        user = request.env['res.users'].sudo().search([('mobile', '=', mobile)], limit=1)
        if not user:
            return {'error': _('No user found with this WhatsApp number.')}

        otp = user.generate_whatsapp_otp()
        _logger.info(f"OTP for {mobile}: {otp}")
        message = _("Your GEODAKI login code is: %s. It will expire in 2 minutes.") % otp
        
        if self._send_whatsapp_message(mobile, message):
            return {'success': True}
        else:
            return {'error': _('Failed to send WhatsApp message. Please try again later.')}

    @http.route('/web/login/whatsapp/verify', type='json', auth="none", methods=['POST'])
    def verify_otp(self, mobile, otp):
        user = request.env['res.users'].sudo().search([
            ('mobile', '=', mobile),
            ('whatsapp_otp', '=', otp),
            ('whatsapp_otp_expiry', '>=', datetime.now())
        ], limit=1)

        if not user:
            return {'error': _('Invalid or expired OTP.')}

        # Clear OTP and expiry
        user.sudo().write({'whatsapp_otp': False, 'whatsapp_otp_expiry': False})
        
        # Authenticate user manually
        request.session.uid = user.id
        request.session.login = user.login
        request.session.session_token = user._compute_session_token(request.session.sid)
        
        return {'success': True, 'redirect': '/web'}

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        response = super(WhatsAppOTPLogin, self).web_login(redirect=redirect, **kw)
        if request.params.get('login_success') and request.session.uid:
            uid = request.session.uid
            user = request.env['res.users'].sudo().browse(uid)
            if user.whatsapp_2fa_enabled and user.mobile:
                # 2FA required. 
                # Logout to clear the session UID for now, but keep track for OTP
                request.session.logout()
                request.session['whatsapp_otp_pending'] = True
                request.session['whatsapp_otp_uid'] = uid
                request.session['whatsapp_otp_mobile'] = user.mobile
                
                # Send OTP
                otp = user.generate_whatsapp_otp()
                _logger.info(f"2FA OTP for {user.mobile}: {otp}")
                message = _("Your GEODAKI login verification code is: %s") % otp
                self._send_whatsapp_message(user.mobile, message)
                
                return request.redirect('/web/login/whatsapp_2fa?redirect=%s' % (redirect or ''))
        return response

    @http.route('/web/login/whatsapp_2fa', type='http', auth="none", website=True)
    def whatsapp_2fa(self, redirect=None, **kw):
        if not request.session.get('whatsapp_otp_pending'):
            return request.redirect('/web/login')
        
        values = {
            'mobile': request.session.get('whatsapp_otp_mobile'),
            'redirect': redirect,
        }
        return request.render('auth_whatsapp_otp.whatsapp_2fa_page', values)

    @http.route('/web/login/whatsapp_2fa/verify', type='json', auth="none", methods=['POST'])
    def verify_whatsapp_2fa(self, otp, redirect=None):
        if not request.session.get('whatsapp_otp_pending'):
            return {'error': _('No pending verification.')}

        uid = request.session.get('whatsapp_otp_uid')
        user = request.env['res.users'].sudo().browse(uid)
        
        if not user or user.whatsapp_otp != otp or (user.whatsapp_otp_expiry and user.whatsapp_otp_expiry < datetime.now()):
            _logger.warning(f"Invalid 2FA OTP attempted for UID {uid}")
            return {'error': _('Invalid or expired OTP.')}

        _logger.info(f"2FA OTP verified for UID {uid}. Re-authenticating...")

        # Clear OTP and pending flag
        user.sudo().write({'whatsapp_otp': False, 'whatsapp_otp_expiry': False})
        request.session.pop('whatsapp_otp_pending')
        request.session.pop('whatsapp_otp_uid')
        request.session.pop('whatsapp_otp_mobile')

        # Re-authenticate the session
        request.session.uid = uid
        request.session.login = user.login
        request.session.session_token = user._compute_session_token(request.session.sid)
        _logger.info(f"Session re-authenticated for {user.login}")

        return {'success': True, 'redirect': redirect or '/web'}
