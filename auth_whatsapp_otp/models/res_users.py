from odoo import models, fields, api
import random
import string
from datetime import datetime, timedelta

class ResUsers(models.Model):
    _inherit = 'res.users'

    whatsapp_otp = fields.Char(string='WhatsApp OTP', copy=False)
    whatsapp_otp_expiry = fields.Datetime(string='WhatsApp OTP Expiry', copy=False)
    whatsapp_2fa_enabled = fields.Boolean(string='WhatsApp 2FA Enabled', default=False)

    def generate_whatsapp_otp(self):
        otp = ''.join(random.choices(string.digits, k=6))
        expiry = datetime.now() + timedelta(minutes=2)
        self.sudo().write({
            'whatsapp_otp': otp,
            'whatsapp_otp_expiry': expiry
        })
        return otp
