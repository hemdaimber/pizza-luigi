(function () {
    var app = angular.module('pizzaSite', ['logistics']);

    app.config(['$interpolateProvider', function ($interpolateProvider) {
        $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');
    }]);

    app.directive('pizzaMobile', function () {
        return {
            restrict: 'A',
            templateUrl: 'pizzas.html',
            controller: ['$http', function ($http) {
                var pizza = this;
                this.pizzas = [];

                this.orderPizzaById = function (pizzaId) {
                    $http.post(
                        '/dishes/pizzas/' + pizzaId + '/discount/' + $('#pizza_discount_' + pizzaId).val().toString(),
                        { date: (new Date()).toLocaleString().hexEncode() }).success(orderFoodCallback);
                };

                this.refreshPizzas = function () {
                    $http.get('/dishes/pizzas/mobile').success(function (data) {
                        pizza.pizzas = data.pizzas;
                    });
                };

                $('#pizzas_li').click(function () {
                    pizza.refreshPizzas();
                });

                this.refreshPizzas();
            }],
            controllerAs: 'pizza'
        };
    });

    app.directive('pizza', function () {
        return {
            restrict: 'A',
            templateUrl: 'pizzas.html',
            controller: ['$http', function ($http) {
                var pizza = this;
                this.pizzas = [];

                this.orderPizzaById = function (pizzaId) {
                    $http.post(
                        '/dishes/pizzas/' + pizzaId + '/discount/' + $('#pizza_discount_' + pizzaId).val().toString(),
                        { date: (new Date()).toLocaleString().hexEncode() }).success(orderFoodCallback);
                };

                this.refreshPizzas = function () {
                    $http.get('/dishes/pizzas').success(function (data) {
                        pizza.pizzas = data.pizzas;
                    });
                };

                $('#pizzas_li').click(function () {
                    pizza.refreshPizzas();
                });

                this.refreshPizzas();
            }],
            controllerAs: 'pizza'
        };
    });

    app.directive('special', function () {
        return {
            restrict: 'A',
            templateUrl: 'specials.html',
            controller: ['$http', function ($http) {
                var alertDiv = '<div class="alert alert-${alertType} alert-dismissable"><button type="button" class="close" data-dismiss="alert"  aria-label="לסגירה"> &times;</button>${msg}</div>';

                var special = this;
                this.specials = [];

                this.orderSpecialById = function (specialId) {
                    var had_special = ($("#order_had_special").val() == 'YES')

                    $http.post('/specials/' + specialId,
                        {
                            date: (new Date()).toLocaleString().hexEncode(),
                            hadSpecial: $("#order_had_special").val()
                        }, { headers: { 'Content-type': 'application/json' } }).success(function (data) {
                            if (data.success) {
                                $("#order_had_special").val('YES')
                            }
                            orderFoodCallback(data);
                        });

                };

                this.refreshSpecials = function () {
                    $http.get('/dishes/specials').success(function (data) {
                        special.specials = data.specials;
                        $("#order_had_special").val(data.had_special);
                    });
                };

                $('#specials_li').click(function () {
                    special.refreshSpecials();
                });

                this.refreshSpecials();
            }],
            controllerAs: 'special'
        };
    });

    app.directive('emails', function () {
        return {
            restrict: 'A',
            templateUrl: 'emails.html',
            controller: ['$http', function ($http) {
                var email = this;
                this.emails = [];

                this.openEmail = function (specialId) {
                    $http.get('/email/' + emailId).success(displayEmail);
                };

                this.refreshEmails = function () {
                    $http.get('/emails').success(function (data) {
                        email.emails = data.emails;
                    });
                };

                $('#inbox').click(function () {
                    special.refreshEmails();
                });

                this.refreshEmails();
            }],
            controllerAs: 'emails'
        };
    });

    app.directive('side', function () {
        return {
            restrict: 'A',
            templateUrl: 'sides.html',
            controller: ['$http', function ($http) {
                var side = this;
                this.sides = [];

                this.orderSideById = function (sideId) {
                    $http.post('/dishes/sides/' + sideId + '/discount/' + $('#side_discount_' + sideId).val().toString(),
                        { date: (new Date()).toLocaleString().hexEncode() }).success(orderFoodCallback);
                };

                this.refreshSides = function () {
                    $http.get('/dishes/sides').success(function (data) {
                        side.sides = data.sides;
                    });
                };

                $('#sides_li').click(function () {
                    side.refreshSides();
                });

                this.refreshSides();
            }],
            controllerAs: 'side'
        };
    });

})();

$(document).ready(function () {
    $('#change_passowrd_but').click(function () {
        $('#pizza_change_password_dialog').modal('show');
    });

    $('#login_but').click(function () {
        $('#pizza_login_dialog').modal('show');
    });

    $('#register_but').click(function () {
        $('#pizza_register_dialog').modal('show');
    });

    $('#charge_account_dialog_but').click(function () {
        $('#charge_account_dialog').modal('show');
    });

    $('#transfer_money_dialog_but').click(function () {
        $('#transfer_money_dialog').modal('show');
    });
});

function toggleEmailBody(emailId, unread) {
    window.location.href = '/messages/' + emailId;
    if (unread) {
        $('#message_id_' + emailId + '_header').removeClass('email_unread');
        var userId = $('#logged_in_user_id').val();
        doJSON('put', '/messages/' + emailId, JSON.stringify({ unread: false }), function (data, status) {
            updateInboxUnread(data.unread_messages);
        });
    }

}

function postForm(path, params, method) {
    method = method || "post";

    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);
    form.form_submit = form.submit;

    for (var key in params) {
        if (params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
        }
    }

    document.body.appendChild(form);
    form.form_submit();
}

function switchDialog(from, to) {
    $('#' + from).modal('hide');
    $('#' + to).modal('show');
}

function updateServerMessage(data) {
    var alertDiv = '<div class="alert server_message ${alertType}"><button type="button" class="close" data-dismiss="alert" aria-label="לסגירה">X</button>${msg}</div>';
    var alertType = null;
    var server_message = null;

    if (data.success) {
        alertType = 'success';
        server_message = data.server_message;
    } else {
        alertType = 'danger';
        server_message = data.err_message;
    }
    $.tmpl(alertDiv, { "alertType": alertType, "msg": server_message }).appendTo("#server_message");
}

function orderFoodCallback(data) {
    // sting data means usually that someone wanted pizza but wasn't logged in
    if (typeof (data) == "string") {
        $('#pizza_login_dialog').modal('show');
    } else {
        updateServerMessage(data);
        updateAccountBalance(data.account_balance);
    }
}

function chargeAccountCallback(data) {
    $('#charge_account_dialog').modal('hide');
    // sting data means usually that someone wanted to charge his account but wasn't logged in
    if (typeof (data) == "string") {
        $('#pizza_login_dialog').modal('show');
    } else {
        updateServerMessage(data);
        updateAccountBalance(data.account_balance);
    }
}
function sendMessageCallback(data) {
    $('#messages_dialog').modal('hide');
    // sting data means usually that someone wanted to send an email but wasn't logged in
    if (typeof (data) == "string") {
        $('#pizza_login_dialog').modal('show');
    } else {
        updateInboxUnread(data.number_of_messages_unread);
        updateServerMessage(data);
    }
}

function TransferMoneyCallback(data) {
    $('#transfer_money_dialog').modal('hide');
    // sting data means usually that someone wanted to transfer money but wasn't logged in
    if (typeof (data) == "string") {
        $('#pizza_login_dialog').modal('show');
    } else {
        updateServerMessage(data);
        updateAccountBalance(data.account_balance);
    }
}

function updateAccountBalance(newBalance) {
    $('#account_balance').text("Current Balance: $" + newBalance);
}

function updateInboxUnread(numUnread) {
    $('#inbox_but').text("Inbox (" + numUnread + ")");
}

function doJSON(methods, url, data, callback) {
    $.ajax({
        'type': methods,
        'url': url,
        'contentType': 'json',
        'data': data,
        'dataType': 'json',
        'success': callback,
        'crossDomain': true
    });
}

String.prototype.hexEncode = function () {
    var hex, i;

    var result = "";
    for (i = 0; i < this.length; i++) {
        hex = this.charCodeAt(i).toString(16);
        result += ("000" + hex).slice(-4);
    }

    return result
};