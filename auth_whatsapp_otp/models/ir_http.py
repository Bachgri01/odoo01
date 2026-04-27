from odoo import models, http
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _auth_method_user(cls):
        super(IrHttp, cls)._auth_method_user()
        if request.session.get('whatsapp_otp_pending'):
            raise http.SessionExpiredException("WhatsApp OTP verification pending")
