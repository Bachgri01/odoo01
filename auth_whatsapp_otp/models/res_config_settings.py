from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_gateway = fields.Selection([
        ('ultramsg', 'UltraMsg'),
        ('twilio', 'Twilio'),
        ('infobip', 'Infobip'),
        ('messagebird', 'MessageBird'),
        ('meta', 'Meta Cloud API (Facebook)'),
    ], string='WhatsApp Gateway', default='ultramsg', config_parameter='auth_whatsapp_otp.whatsapp_gateway')

    ultramsg_instance_id = fields.Char(string='UltraMsg Instance ID', config_parameter='auth_whatsapp_otp.ultramsg_instance_id')
    ultramsg_token = fields.Char(string='UltraMsg Token', config_parameter='auth_whatsapp_otp.ultramsg_token')

    twilio_account_sid = fields.Char(string='Twilio Account SID', config_parameter='auth_whatsapp_otp.twilio_account_sid')
    twilio_auth_token = fields.Char(string='Twilio Auth Token', config_parameter='auth_whatsapp_otp.twilio_auth_token')
    twilio_phone_number = fields.Char(string='Twilio WhatsApp Number', config_parameter='auth_whatsapp_otp.twilio_phone_number', help="Format: whatsapp:+1234567890")

    infobip_base_url = fields.Char(string='Infobip Base URL', config_parameter='auth_whatsapp_otp.infobip_base_url', help="Example: https://xyz.api.infobip.com")
    infobip_api_key = fields.Char(string='Infobip API Key', config_parameter='auth_whatsapp_otp.infobip_api_key')
    infobip_sender = fields.Char(string='Infobip Sender Number', config_parameter='auth_whatsapp_otp.infobip_sender')

    messagebird_api_key = fields.Char(string='MessageBird API Key', config_parameter='auth_whatsapp_otp.messagebird_api_key')
    messagebird_channel_id = fields.Char(string='MessageBird Channel ID', config_parameter='auth_whatsapp_otp.messagebird_channel_id')

    meta_api_token = fields.Char(string='Meta API Token', config_parameter='auth_whatsapp_otp.meta_api_token')
    meta_phone_number_id = fields.Char(string='Meta Phone Number ID', config_parameter='auth_whatsapp_otp.meta_phone_number_id')
    whatsapp_otp_expiry_minutes = fields.Integer(string='OTP Expiry (Minutes)', config_parameter='auth_whatsapp_otp.expiry_minutes', default=2)
