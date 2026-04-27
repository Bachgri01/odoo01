/** @odoo-module **/

import publicWidget from 'web.public.widget';
import { _t } from 'web.core';

publicWidget.registry.WhatsAppLogin = publicWidget.Widget.extend({
    selector: '.oe_login_form, .oe_whatsapp_login_form, .oe_login_form_box',
    events: {
        'click #btn_toggle_whatsapp': '_onToggleWhatsApp',
        'click #btn_back_to_login': '_onBackToLogin',
        'click #btn_send_otp': '_onSendOtp',
        'click #btn_verify_otp': '_onVerifyOtp',
        'click #btn_resend_otp': '_onResendOtp',
    },

    init: function () {
        this._super.apply(this, arguments);
        this.timerInterval = null;
    },

    start: function () {
        console.log("WhatsApp Login Widget Started", this.$el);
        this.$standardForm = $('#standard_login_form');
        this.$whatsappForm = $('#whatsapp_login_form');
        this.$btnToggle = $('#btn_toggle_whatsapp');
        this.$mobileInput = $('#whatsapp_mobile');
        this.$otpInput = $('#whatsapp_otp');
        this.$otpSection = $('#otp_section');
        this.$timerSpan = $('#otp_timer');
        this.$errorAlert = $('#whatsapp_error');
        this.$successAlert = $('#whatsapp_success');
        this.$btnSend = $('#btn_send_otp');
        this.$btnVerify = $('#btn_verify_otp');
        this.$btnResend = $('#btn_resend_otp');

        return this._super.apply(this, arguments);
    },

    _onToggleWhatsApp: function (ev) {
        ev.preventDefault();
        console.log("Toggle Clicked");
        this.$standardForm.addClass('d-none');
        this.$whatsappForm.removeClass('d-none');
        // Hide the toggle button container
        $('.whatsapp_login_options').first().addClass('d-none');
    },

    _onBackToLogin: function (ev) {
        ev.preventDefault();
        this.$standardForm.removeClass('d-none');
        this.$whatsappForm.addClass('d-none');
        $('.whatsapp_login_options').first().removeClass('d-none');
        this._resetForm();
    },

    _resetForm: function () {
        this.$errorAlert.addClass('d-none');
        this.$successAlert.addClass('d-none');
        this.$otpSection.addClass('d-none');
        this.$btnVerify.addClass('d-none');
        this.$btnResend.addClass('d-none');
        this.$btnSend.removeClass('d-none');
        this.$mobileInput.prop('disabled', false);
        clearInterval(this.timerInterval);
    },

    _startTimer: function (duration) {
        let timer = duration, minutes, seconds;
        clearInterval(this.timerInterval);
        this.timerInterval = setInterval(() => {
            minutes = parseInt(timer / 60, 10);
            seconds = parseInt(timer % 60, 10);

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            this.$timerSpan.text(minutes + ":" + seconds);

            if (--timer < 0) {
                clearInterval(this.timerInterval);
                this._showError(_t("OTP expired. Please resend."));
                this.$btnVerify.prop('disabled', true);
                this.$btnResend.removeClass('d-none');
            }
        }, 1000);
    },

    _onSendOtp: function (ev) {
        ev.preventDefault();
        const mobile = this.$mobileInput.val();
        if (!mobile) {
            this._showError(_t("Please enter your WhatsApp number."));
            return;
        }

        this.$errorAlert.addClass('d-none');
        this.$btnSend.prop('disabled', true);

        this._rpc({
            route: '/web/login/whatsapp/send_otp',
            params: { mobile: mobile },
        }).then((result) => {
            if (result.error) {
                this._showError(result.error);
                this.$btnSend.prop('disabled', false);
            } else {
                this._showSuccess(_t("Code sent to your WhatsApp!"));
                this.$otpSection.removeClass('d-none');
                this.$btnSend.addClass('d-none');
                this.$btnVerify.removeClass('d-none').prop('disabled', false);
                this.$mobileInput.prop('disabled', true);
                this._startTimer(120); // 2 minutes
            }
        }).catch((err) => {
            console.error("RPC Error", err);
            this._showError(_t("An error occurred. Please try again."));
            this.$btnSend.prop('disabled', false);
        });
    },

    _onResendOtp: function (ev) {
        ev.preventDefault();
        this._onSendOtp(ev);
        this.$btnResend.addClass('d-none');
    },

    _onVerifyOtp: function (ev) {
        ev.preventDefault();
        const mobile = this.$mobileInput.val();
        const otp = this.$otpInput.val();
        
        if (!otp) {
            this._showError(_t("Please enter the OTP."));
            return;
        }

        this.$errorAlert.addClass('d-none');
        this.$btnVerify.prop('disabled', true);

        this._rpc({
            route: '/web/login/whatsapp/verify',
            params: { mobile: mobile, otp: otp },
        }).then((result) => {
            if (result.error) {
                this._showError(result.error);
                this.$btnVerify.prop('disabled', false);
            } else {
                window.location.href = result.redirect || '/web';
            }
        }).catch((err) => {
            console.error("RPC Error", err);
            this._showError(_t("Verification failed."));
            this.$btnVerify.prop('disabled', false);
        });
    },

    _showError: function (msg) {
        this.$errorAlert.text(msg).removeClass('d-none');
        this.$successAlert.addClass('d-none');
    },

    _showSuccess: function (msg) {
        this.$successAlert.text(msg).removeClass('d-none');
        this.$errorAlert.addClass('d-none');
    }
});

export default publicWidget.registry.WhatsAppLogin;

publicWidget.registry.WhatsApp2FA = publicWidget.Widget.extend({
    selector: '.oe_whatsapp_2fa_form',
    events: {
        'click #btn_verify_2fa': '_onVerify2fa',
    },

    _onVerify2fa: function (ev) {
        ev.preventDefault();
        const otp = this.$('#whatsapp_2fa_otp').val();
        const redirect = this.$('input[name="redirect"]').val();

        if (!otp) return;

        this.$('#btn_verify_2fa').prop('disabled', true);
        this.$('#whatsapp_2fa_error').addClass('d-none');

        this._rpc({
            route: '/web/login/whatsapp_2fa/verify',
            params: {
                otp: otp,
                redirect: redirect,
            },
        }).then((result) => {
            console.log("2FA Verification Result:", result);
            if (result.error) {
                this.$('#whatsapp_2fa_error').text(result.error).removeClass('d-none');
                this.$('#btn_verify_2fa').prop('disabled', false);
            } else {
                console.log("Redirecting to:", result.redirect || '/web');
                window.location.href = result.redirect || '/web';
            }
        }).catch((err) => {
            console.error("2FA RPC Error:", err);
            this.$('#whatsapp_2fa_error').text(_t("Verification failed.")).removeClass('d-none');
            this.$('#btn_verify_2fa').prop('disabled', false);
        });
    },
});
