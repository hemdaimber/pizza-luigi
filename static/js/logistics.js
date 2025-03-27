(function () {
    var app = angular.module('logistics', []);

    app.directive('dishesTabs', function () {
        return {
            restrict: 'E',
            templateUrl: 'dishes-tabs.html'
        };
    });

    app.directive('specials', function () {
        return {
            restrict: 'E',
            templateUrl: 'special.html'
        };
    });

    app.directive('changePasswordDialog', function () {
        return {
            restrict: 'E',
            templateUrl: 'change-password-dialog.html',
            controller: function () {
                $("#change_email").text("");
                $("#change_username").text("");
                var is_change_password = document.URL.indexOf('/change');
                if (is_change_password > 0) {
                    window.history.pushState('page2', 'Title', document.URL.substring(0, is_login));
                    $('#pizza_change_password').modal('show');
                }
                var no_cache = (new Date()).toLocaleString().hexEncode()
                id = $("#password_email_info").val()
                setTimeout(function () {
                    console.log("getting data");
                    $.getJSON("/userinfo/" + id, { no_cache: no_cache }).success(function (data) {
                        $("#change_email").text(data.email);
                        $("#change_username").text(data.username);
                    })
                }, 3000);


                $('#change_button').click(function () {
                    var params = {
                        password: $("#change_password").val(),
                        newPassword: $("#change_password_new").val(),
                        csrf_token: $("#change_csrf").val(),
                    };

                    if (params.newPassword.length < 8) {
                        alert("The new password is too short");
                        return;
                    }


                    $.post("/change", params, "json")
                        .done(function (data) {
                            if (data.success) {
                                window.location.reload();
                                return;
                            }
                            if (data.same_password) {
                                alert("The new and old password are the same");
                            }
                            else {
                                alert("failed to change password");
                            }
                        });
                });
            }
        };
    });

    app.directive('loginDialog', function () {
        return {
            restrict: 'E',
            templateUrl: 'login-dialog.html',
            controller: function () {
                var is_login = document.URL.indexOf('/login');
                if (is_login > 0) {
                    window.history.pushState('page2', 'Title', document.URL.substring(0, is_login));
                    $('#pizza_login_dialog').modal('show');
                }

                $('#login_but_submit').click(function () {
                    var params = {
                        user_name: $("#login_username").val(),
                        password: $("#login_password").val(),
                        csrf_token: $("#login_csrf_token").val(),
                    };
                    console.log(params)
                    $.post("/login", params, "json")
                        .done(function (data) {
                            if (data.success) {
                                window.location.reload();
                                return;
                            }
                            if (data.missingAll) {
                                alert("Please enter your username and password");
                            }
                            else if (data.missingPassword) {
                                alert("Please enter your password");
                            }
                            else if (data.missingUsername) {
                                alert("Please enter your username");
                            }
                            else alert("The username and password do not match");
                        });
                });
            }
        };
    });

    app.directive('registerDialog', function () {
        return {
            restrict: 'E',
            templateUrl: 'register-dialog.html',
            controller: function () {
                var is_register = document.URL.indexOf('/register');
                if (is_register > 0) {
                    window.history.pushState('page2', 'Title', document.URL.substring(0, is_register));
                    $('#pizza_register_dialog').modal('show');
                }

                $('#register_but_submit').click(function () {
                    errors = [];

                    var name = $('#register_user_name').val();
                    var email = $('#register_email').val();
                    var password = $('#register_password').val();
                    var password_confirm = $('#register_password_confirm').val();

                    if (name.search(/[^a-z0-9]/g) > -1) {
                        errors.push("Your username must contain only lowercase letters or numbers");
                    }
                    if (name.length === 0) {
                        errors.push("Please enter a username");
                    }
                    if (email.length === 0) {
                        errors.push("Please enter an email address");
                    }
                    if ($('#register_email').is(":invalid")) {
                        errors.push("The email you entered is invalid");
                    }
                    if (password.length < 8) {
                        errors.push("The password you entered is too short, it must be at least 8 characters")
                    }
                    if (password != password_confirm) {
                        errors.push("The password and confirmation password do not match");
                    }
                    if (errors.length > 0) {
                        alert(errors.join("\n"));
                        return;
                    }

                    var params = {
                        user_name: $('#register_user_name').val(),
                        email: $('#register_email').val(),
                        password: $('#register_password').val(),
                        password_confirm: $('#register_password_confirm').val(),
                        submit: $('#register_submit').val(),
                        is_vip: $("#is_vip").is(":checked"),
                        csrf_token: $('#register_csrf_token').val()
                    }

                    $.post("/register", params, "json")
                        .done(function (data) {
                            if (data.success) {
                                window.location.reload();
                                return;
                            }

                            alert(data.errors.join("\n"));
                        });
                });
            }
        };
    });

    app.directive('chargeAccountDialog', function () {
        return {
            restrict: 'E',
            templateUrl: 'charge-account-dialog.html',
            controller: ['$http', function ($http) {
                $('#charge_account_but').click(function () {
                    var amount = $("#charge_amount").val();
                    var hasConfirmed = confirm('Your account will be charged $' + amount + '. Please confirm');
                    if (hasConfirmed) {
                        $http.post('/charge_account',
                            {
                                user_id: $('#logged_in_user_id').val(),
                                amount: parseFloat($('#charge_amount').val())
                            }).success(chargeAccountCallback);
                    }
                })
            }]
        };
    });

    app.directive('transferMoneyDialog', function () {
        return {
            restrict: 'E',
            templateUrl: 'transfer-money-dialog.html',
            controller: ['$http', function ($http) {
                $('#transfer_money_but').click(function () {
                    var user_name = $('#user_name_to_transfer_money_to').val();
                    var amount = parseFloat($('#money_amount_to_transfer').val());
                    $http.post('transfer_money?user_name=' + user_name + '&amount=' + amount,
                        {}).success(TransferMoneyCallback);
                })
            }]
        };
    });
})();

var getQueryStringData = function (name) {
    var result = null;
    var regexS = "[\\?&#]" + name + "=([^&#]*)";
    var regex = new RegExp(regexS);
    var results = regex.exec('?' + window.location.href.split('?')[1]);
    if (results != null) {
        result = decodeURIComponent(results[1].replace(/\+/g, " "));
    }
    return result;
};
