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
        """Main dispatcher for sending WhatsApp messages"""
        ICP = request.env['ir.config_parameter'].sudo()
        gateway = ICP.get_param('auth_whatsapp_otp.whatsapp_gateway', 'ultramsg')

        if gateway == 'ultramsg':
            return self._send_ultramsg_message(mobile, message)
        elif gateway == 'twilio':
            return self._send_twilio_message(mobile, message)
        elif gateway == 'infobip':
            return self._send_infobip_message(mobile, message)
        elif gateway == 'messagebird':
            return self._send_messagebird_message(mobile, message)
        elif gateway == 'meta':
            return self._send_meta_message(mobile, message)
        
        _logger.error(f"Unknown WhatsApp gateway: {gateway}")
        return False

    def _send_ultramsg_message(self, mobile, message):
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
            _logger.error(f"UltraMsg Sending Error: {str(e)}")
            return False

    def _send_twilio_message(self, mobile, message):
        """Helper to send WhatsApp message via Twilio"""
        ICP = request.env['ir.config_parameter'].sudo()
        account_sid = ICP.get_param('auth_whatsapp_otp.twilio_account_sid')
        auth_token = ICP.get_param('auth_whatsapp_otp.twilio_auth_token')
        from_number = ICP.get_param('auth_whatsapp_otp.twilio_phone_number')

        if not account_sid or not auth_token or not from_number:
            _logger.error("Twilio SID, Token or Phone Number not configured.")
            return False

        import requests
        from requests.auth import HTTPBasicAuth
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        
        # Ensure mobile is in international format with whatsapp: prefix for Twilio
        to_number = mobile
        if not to_number.startswith('whatsapp:'):
            to_number = f"whatsapp:{to_number}"

        payload = {
            "From": from_number,
            "To": to_number,
            "Body": message
        }
        
        try:
            response = requests.post(url, data=payload, auth=HTTPBasicAuth(account_sid, auth_token))
            if response.status_code in [200, 201]:
                return True
            _logger.error(f"Twilio Error: {response.text}")
            return False
        except Exception as e:
            _logger.error(f"Twilio Sending Error: {str(e)}")
            return False

    def _send_infobip_message(self, mobile, message):
        """Helper to send WhatsApp message via Infobip"""
        ICP = request.env['ir.config_parameter'].sudo()
        base_url = ICP.get_param('auth_whatsapp_otp.infobip_base_url')
        api_key = ICP.get_param('auth_whatsapp_otp.infobip_api_key')
        sender = ICP.get_param('auth_whatsapp_otp.infobip_sender')

        if not base_url or not api_key or not sender:
            _logger.error("Infobip Base URL, API Key or Sender not configured.")
            return False

        import requests
        url = f"{base_url.rstrip('/')}/whatsapp/1/message/text"
        
        payload = {
            "from": sender,
            "to": mobile.lstrip('+'), # Infobip usually wants number without +
            "content": {"text": message}
        }
        headers = {
            "Authorization": f"App {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                return True
            _logger.error(f"Infobip Error: {response.text}")
            return False
        except Exception as e:
            _logger.error(f"Infobip Sending Error: {str(e)}")
            return False

    def _send_messagebird_message(self, mobile, message):
        """Helper to send WhatsApp message via MessageBird"""
        ICP = request.env['ir.config_parameter'].sudo()
        api_key = ICP.get_param('auth_whatsapp_otp.messagebird_api_key')
        channel_id = ICP.get_param('auth_whatsapp_otp.messagebird_channel_id')

        if not api_key or not channel_id:
            _logger.error("MessageBird API Key or Channel ID not configured.")
            return False

        import requests
        url = "https://conversation.messagebird.com/v1/send"
        
        payload = {
            "to": mobile.lstrip('+'),
            "from": channel_id,
            "type": "text",
            "content": {"text": message}
        }
        headers = {
            "Authorization": f"AccessKey {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201, 202, 204]:
                return True
            _logger.error(f"MessageBird Error: {response.text}")
            return False
        except Exception as e:
            _logger.error(f"MessageBird Sending Error: {str(e)}")
            return False

    def _send_meta_message(self, mobile, message):
        """Helper to send WhatsApp message via Meta Cloud API"""
        ICP = request.env['ir.config_parameter'].sudo()
        token = ICP.get_param('auth_whatsapp_otp.meta_api_token')
        phone_id = ICP.get_param('auth_whatsapp_otp.meta_phone_number_id')

        if not token or not phone_id:
            _logger.error("Meta API Token or Phone ID not configured.")
            return False

        import requests
        url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
        
        # NOTE: Meta Cloud API usually requires using TEMPLATES for initiated messages.
        # However, for testing or if the 24h window is open, text can work.
        # For OTP, it's best to use a template named 'otp' or similar.
        # Here we attempt a free-form text message.
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile.lstrip('+'),
            "type": "text",
            "text": {"body": message}
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                return True
            _logger.error(f"Meta Error: {response.text}")
            return False
        except Exception as e:
            _logger.error(f"Meta Sending Error: {str(e)}")
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
