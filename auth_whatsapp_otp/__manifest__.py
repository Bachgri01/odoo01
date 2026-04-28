{
    'name': 'WhatsApp OTP Authentication',
    'version': '1.0',
    'license': 'OPL-1',
    'category': 'setting',
    'summary': 'Login via WhatsApp OTP using multiple gateways',
    'price': 9.99,
    'currency': 'EUR',
    'description': """
        This module allows users to log in using a one-time password sent via WhatsApp.
        It uses multiple gateways API for sending messages.
    """,
    'depends': ['base', 'web'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
        'views/login_templates.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
        'static/description/main_1.png',
        'static/description/main_2.png',
    ],
    'assets': {
        'web.assets_frontend': [
            'auth_whatsapp_otp/static/src/css/whatsapp_login.css',
            'auth_whatsapp_otp/static/src/js/whatsapp_login.js',
        ],
    },
    'installable': True,
    'application': False,
}
