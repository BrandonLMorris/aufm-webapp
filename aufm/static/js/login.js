AUFM = {
    Login: {
        setup: function() {
            $('#login_button').click(this.events.login);
            $('#forgot_button').click(this.events.forgot);
            $('#forgot_submit').click(this.events.submit);
            $('#forgot_cancel').click(this.events.cancel);
        },
        events: {
            login: function(e) {
                var email = $('#login_email').val();
                var password = $('#login_password').val();
                if(email.length == 0) {
                    $('#login_email').addClass("invalid");
                    return;
                }
                if(password.length == 0) {
                    $('#login_password').addClass("invalid");
                    return;
                }
                AUFM.Util.api({
                    url: "login",
                    type: "POST",
                    data: { "email": email, "password": password },
                    callback: function(data) {
                        if(data.error) {
                            console.log(data.error);
                            return;
                        }
                        location.href = "/";
                    },
                });
            },
            forgot: function(e) {
                $('#email_row, #login_buttons').hide();
                $('#forgot_buttons').show();
            },
            submit: function(e) {
                var email = $('#login_email').val();
                if(email.length == 0) {
                    $('#login_email').addClass("invalid");
                    return;
                }
                AUFM.Util.api({
                    url: "request-password-reset",
                    type: "POST",
                    data: { "email": email },
                    callback: function(data) {
                        if(data.error) {
                            console.log(data.error);
                            return;
                        }
                        Materialize.toast('Password reset sent!', 4000);
                        AUFM.Login.events.cancel();
                    },
                });
            },
            cancel: function(e) {
                $('#email_row, #login_buttons').show();
                $('#forgot_buttons').hide();
            },
        },
    },
};

$(document).ready((e) => {
    AUFM.Login.setup();
});