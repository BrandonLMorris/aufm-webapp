AUFM = {
    Login: {
        setup: function() {
            $('#login_button').click(this.events.login);
            $('#forgot_button').click(this.events.forgot);
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

            },
        },
    },
};

$(document).ready((e) => {
    AUFM.Login.setup();
});