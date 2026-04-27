from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ultramsg_instance_id = fields.Char(string='UltraMsg Instance ID', config_parameter='auth_whatsapp_otp.ultramsg_instance_id')
    ultramsg_token = fields.Char(string='UltraMsg Token', config_parameter='auth_whatsapp_otp.ultramsg_token')
    whatsapp_otp_expiry_minutes = fields.Integer(string='OTP Expiry (Minutes)', config_parameter='auth_whatsapp_otp.expiry_minutes', default=2)
