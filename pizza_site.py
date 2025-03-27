import datetime
import json
import logging
import os
import time
import re

from functools import wraps
from itertools import chain
from logging.handlers import WatchedFileHandler

import flask
from werkzeug.datastructures import MultiDict, TypeConversionDict
from werkzeug.routing import BaseConverter
from app_factory import app
from models import db
from flask import render_template, jsonify, request, redirect, url_for, g
from flask_security.forms import Required	
from flask_security import Security, SQLAlchemyUserDatastore, utils	
from flask_wtf import Form	
from flask_wtf.csrf import generate_csrf
from flask_security.forms import RegisterForm, LoginForm
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from dateutil import parser

from models.Session import UserSession


__all__ = ["User", "Message", "Food", "Role"]

# 20% discount
VIP_DISCOUNT = 0.2

# 20% discount
MANAGER_DISCOUNT = 1

IS_SQL_INJECTION = False
#check if magshimim project of WEB SEC project
with open('./config.json') as file:
    IS_SQL_INJECTION = json.load(file)['isSQLinjection']


# Create app
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import TextField

logformat = ('%(asctime)s %(filename)s %(lineno)s %(process)d %(levelname)s:  %(message)s')
log_level = logging.INFO
logging.basicConfig(format=logformat, level=log_level)
handler = WatchedFileHandler(filename="/tmp/pizza_site.log")
handler.setFormatter(logging.Formatter(fmt=logformat))
logging.getLogger().addHandler(handler)
logging.log(1, "server started")

####################################
############   MODELs  #############
####################################
from models.message import Message
from models.food import Food, FoodType, FoodOrder
from models.users import User, Role


class ExtendedRegisterForm(RegisterForm):
    user_name = TextField('User Name', [Required()])
    is_vip = BooleanField('VIP User', [])

    def validate(self):
        # Use standard validator
        validation = RegisterForm.validate(self)
        validation_result = validateUser(self.data["user_name"], self.data["email"])
        try:
            self.email.errors.remove(self.data["email"]+" is already associated with an account.")
        except:
            pass
        if "Invalid email address" in self.email.errors:
            self.email.errors.remove("Invalid email address")
            self.email.errors.append("The email you entered is invalid")
        if validation_result["is_user_taken"]:
            self.email.errors.append("The username "+self.data["user_name"]+" you entered is already taken, please choose another one")
        if validation_result["is_email_taken"]:
            self.email.errors.append("The email "+self.data["email"]+" you entered is already associated with another account")

        if self.is_vip.data is None:
            self.is_vip.errors.append("no vip data")
            validation = False

        return validation_result["success"] and validation


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class ExtendedLoginForm(LoginForm):
    user_name = TextField('User Name:', [Required()])


app.config['DEFAULT_REMEMBER_ME'] = False
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

app.config['SECURITY_REGISTER_URL'] = '/blablablablablablablabla'
app.config['SECURITY_LOGIN_URL'] = '/blablablablablablablabla2'
app.config['SECURITY_LOGOUT_URL'] = '/blablablablablablablabla3'
app.config['SECURITY_CHANGE_URL'] = '/blablablablablablablabla3'
app.config['SESSION_COOKIE_NAME'] = 'junkyardofsessionable'
app.config['SESSION_COOKIE_HTTPONLY'] = True

security = Security(app, user_datastore, register_form=ExtendedRegisterForm)

tst = app.process_response


# this is here to remove the extra session set by flask-security
def wraping(response):
    resp = tst(response)
    for v in response.headers._list:
        if 'junkyardofsessionable' in v[1]:
            response.headers._list.remove(v)
    return resp


app.process_response = wraping


####################################
############   before/after  ###############
####################################

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.is_logged_in:
            return redirect(url_for('Home'))
        return f(*args, **kwargs)

    return decorated_function


# Logging
#########
def LogRequestDuration(func):
    @wraps(func)
    def TimeTheFunction(*args, **kwargs):
        # start_ts = time.time()
        resp = func(*args, **kwargs)
        # end_ts = time.time()
        # logging.info("{!s} took {!s} seconds to run".format(func.__name__, round(end_ts - start_ts, 3)))
        return resp

    return TimeTheFunction

def emptyDB():
    db.session.query(Message).delete()
    db.session.query(FoodOrder).delete()
    db.session.query(UserSession).delete()
    db.session.query(User).delete()
    db.session.query(Role).delete()
    db.session.query(Food).delete()
    db.session.commit()

#This must be removed!
# emptyDB()

def init_db():
    print("Initializing!!")
    admin_role = user_datastore.create_role(name='vip', description='Pizza VIP')

    first_user = user_datastore.create_user(email='getpizza@pizzaluigi.pw', user_name="pizzaluigi", is_vip=True,
                                            password=utils.encrypt_password('pa55word'))
    second_user = user_datastore.create_user(email='lior@pizzaplace.com', user_name="garso",
                                             password=utils.encrypt_password('pa55word'))
    antonio = user_datastore.create_user(email='antonio7@gmail.com', user_name="antonio7",
                                             password='An7on!0HasaGreatP455')
    mariano = user_datastore.create_user(email='mariano@gmail.com', user_name="mariano",
                                            password='SupErMar!0isTheB0ss')
    Dani = user_datastore.create_user(email='dani@gmail.com', user_name="danir",
                                            password=12345678)

    antonio_id = User.query.filter_by(user_name="antonio7").one().id
    mariano_id = User.query.filter_by(user_name="mariano").one().id

    # admin_id = User.query.filter_by(user_name="pizzaluigi").one().id
    message = Message.FromDict(dict(
        from_user_id=mariano_id,
        to_user_id=antonio_id,
        subject="robbery",
        message_text="""Hi Antonio,<br/><br/>
                        We are so lucky that the police didn't catch us after the robbery! <br/><br/>
                        I kept our <b>1555554</b> dollars in a bag. You'll get your share as soon as I get to Milan. <br/><br/>
                        See you soon,<br/><br/>
                        Mario"""
    ))

    db.session.add(message)

    # db.session.commit()

    db.session.add_all([        	
        Food(type=FoodType.PIZZA, image_url="ROMA pizza.png", food_name="Pizza Roma", price_in_dollars=10,	
             id=554793),	
        Food(type=FoodType.PIZZA, image_url="VENIVE pizza.png", food_name="Pizza Venezia", price_in_dollars=15,	
             id=6979634),	
        Food(type=FoodType.PIZZA, image_url="TOSCANNA pizza.png", food_name="Pizza Toscana", price_in_dollars=20,	
             id=7354477),	
        Food(type=FoodType.SIDE, image_url="cola2.png", food_name="Coke 0.5L", price_in_dollars=3,	
             id=5698744),	
        Food(type=FoodType.SIDE, image_url="icecream.png", food_name="Ice Cream", price_in_dollars=5,	
             id=6546869),	
        Food(type=FoodType.SIDE, image_url="garlic-bread.png", food_name="Garlic Bread", price_in_dollars=7,	
             id=7346795),
        Food(type=FoodType.SALE, image_url="AMERICA pizza.png", food_name="Pizza America", price_in_dollars=5,
             id=9574123),
        Food(type=FoodType.SPECIAL, image_url="TOSCANNA pizza.png", food_name="Pizza Toscana", price_in_dollars=5,
             id=1337)
    ])

    db.session.commit()

@app.before_first_request
def create_user():
    db.create_all()
    if not user_datastore.get_user('getpizza@pizzaluigi.pw'):
        emptyDB()
        init_db()


class AnonymousAccess(object):
    def __init__(self):
        self.id = 0
        self.email = ""
        self.is_vip = False
        self.user_name = "Nobody"
        self.had_special = False
        self.account_balance =0


def is_closed():
    return os.path.exists('lockfile')


@app.before_request
def pre_request_setup():
    if is_closed() and 'adminify' not in request.path:
        return "server is down for maintenance"
    flask.session = None
    sesKey = request.cookies.get("pizza_session")
    sessionObject = UserSession.query.filter_by(key=sesKey).first()
    if sessionObject:
        g.current_user = User.query.filter_by(id=sessionObject.user_id).one()
        g.is_logged_in = True
        g.session_key = sesKey
    else:
        if sesKey:
            resp = redirect(url_for("Home"))
            resp.set_cookie("pizza_session", value='', expires=0)
            return resp
        g.current_user = AnonymousAccess()
        g.is_logged_in = False
        g.session_key = sesKey


def GetUserNavBarParams(user):
    """Returns a dict with the user's Nav Bar data, if the user is logged in
    """
    user_params = dict(
        user_id=None,
        user_is_vip=None,
        user_name=None,
        user_balance=None,
        num_unread_messages=None
    )

    if g.is_logged_in:
        user_params['user_id'] = user.id
        user_params['user_is_vip'] = user.is_vip
        user_params['user_name'] = user.user_name
        user_params['user_balance'] = user.account_balance
        user_params['num_unread_messages'] = len([message for message in user.messages_received if message.unread])

    return user_params


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


def validateUser(user_name, email):
    print "in validate user", user_name, email
    if not (user_name or email):
        return dict(is_user_taken=False, is_email_taken=False, success=False)

    found_user = User.query.filter_by(user_name=user_name).first() is not None
    found_email = User.query.filter_by(email=email).first() is not None

    print "found user", found_user
    print "found email", found_email
    return dict(is_user_taken=found_user, is_email_taken=found_email, success=not (found_user or found_email))


@app.route('/validate/unique')
def validateRegistration():
    user_name = request.args["username"]
    email = request.args["email"]
    return jsonify(validateUser(user_name, email))


@app.route('/')
@LogRequestDuration
def Home():
    user_data_dict = GetUserNavBarParams(g.current_user)
    response = app.make_response(render_template('index.html', **user_data_dict))

    # planting a discount cookie which can be changed by proxy to get users more discounts
    if user_data_dict['user_id']:
        if "user_level" not in request.cookies or request.cookies['user_level'] == "":
            response.set_cookie("user_level", value='3' if user_data_dict['user_is_vip'] else '0',
                                expires=datetime.datetime.utcnow() + datetime.timedelta(weeks=1))
        response.set_cookie("pizza_user_name", value=user_data_dict['user_name'],
                            expires=datetime.datetime.utcnow() + datetime.timedelta(weeks=1))
        response.set_cookie("pizza_user_id", value=str(user_data_dict['user_id']),
                            expires=datetime.datetime.utcnow() + datetime.timedelta(weeks=1))
    else:
        if 'user_level' in request.cookies:
            response.set_cookie("user_level", value='', expires=0)
        if 'pizza_user_name' in request.cookies:
            response.set_cookie("pizza_user_name", value="", expires=0)
        if 'pizza_id' in request.cookies:
            response.set_cookie("pizza_user_id", value="", expires=0)
        if 'session' in request.cookies:
            response.set_cookie("session", value="", expires=0)


    return response


#################################################
#########      ACCOUNT REQUESTS      ############
#################################################

@app.route('/charge_account', methods=['POST'])
@login_required
@LogRequestDuration
def ChargeAccount():
    user = User.query.filter_by(id=g.current_user.id).one()
    err_message = None

    desired_amount = float(request.json['amount'])
    user.account_balance += desired_amount
    db.session.commit()
    return jsonify(dict(success=True,
                        server_message="You added ${!s} to your account".format(desired_amount),
                        err_message=err_message,
                        account_balance=user.account_balance))


@app.route('/<regex("(\w+/)?"):prefix>transfer_money', methods=['POST', 'GET'])
@login_required
@LogRequestDuration
def TransferMoneyToAccount(prefix):
    user = g.current_user
    err_message = None
    server_message = None
    amount = float(request.args['amount'])
    user_name = request.args['user_name']	

    try:
        if amount < 0:
            err_message = "Oooops, you cannot transfer a negative amount of dollars"
            success = False
        elif amount == 0:
            err_message = "Oooops, you cannot transfer zero dollars"
            success = False
        elif user_name == user.user_name:	
            err_message = "Sorry, you cannot transfer money to yourself"
            success = False
        elif user.account_balance < amount:
            err_message = "Sorry, you cannot transfer more money than you have"
            success = False
        else:
            receiver = User.query.filter_by(user_name=user_name).one()	
            receiver.account_balance += amount
            user.account_balance -= amount
            db.session.commit()
            success = True
            server_message = (("You have successfully transferred ${!s} to {!s} ").format(amount, receiver.user_name))
    except (NoResultFound, MultipleResultsFound), e:
        err_message = "Sorry, could not find the user you entered"
        success = False
    return jsonify(dict(success=success,
                        server_message=server_message,
                        err_message=err_message,
                        account_balance=user.account_balance))


#################################################
#########      FOOD REQUESTS        #############
#################################################

@app.route('/mobile_promotion', methods=['GET'])
@LogRequestDuration
def GetMobilePromotion():
    user_data_dict = GetUserNavBarParams(g.current_user)
    
    #here need to be is *not* None
    if re.search(r'getpizza', request.headers.get('User-Agent'), re.IGNORECASE) is not None:
        return render_template('mobile-index.html', **user_data_dict)

    else:
        return render_template('forbidden.html', **user_data_dict)


@app.route('/history', methods=['GET'])
@login_required
@LogRequestDuration
def OrderHistory():
    # We pretend we don't know which user sent this request and
    # instead, we use 'requested_user_id'
    requested_user_id = int(request.args['get'])
    user_data_dict = GetUserNavBarParams(g.current_user)

    user_name = "<User Does Not Exist Exception>"
    order_history = dict()
    try:
        found_user = User.query.filter_by(id=requested_user_id).one()
        if found_user:
            order_history = [order.ToDict() for order in found_user.order_history]
            user_name = found_user.user_name
            order_history.reverse()
    except (NoResultFound, MultipleResultsFound), e:
        order_history = dict()
    user_data_dict.update(dict(order_history=order_history, order_user_name=user_name))

    return render_template('order_history.html', **user_data_dict)


@app.route('/specials/<food_id>', methods=['POST'])
@login_required
@LogRequestDuration
def OrderSpecialFood(food_id):
    had_special = request.json.get('hadSpecial')
    if had_special == 'YES':
        msg = "Sorry, you can get this special offer only once"
        balance = g.current_user.account_balance
        return jsonify(dict(success=False, had_special='YES', err_message=msg,account_balance=balance))
    res = OrderFood(FoodType.SPECIAL, food_id, 0, True)
    if res["success"]:
        user = User.query.filter_by(id=g.current_user.id).one()
        user.had_special = True
        db.session.commit()
    return jsonify(res)


@app.route('/dishes/<food_type>/<food_id>/discount/<discount>', methods=['POST'])
@login_required
@LogRequestDuration
def OrderFood(food_type, food_id, discount, inner=False):
    USER_MAX_ORDER = 100
    user = g.current_user
    err_message = None
    server_message = None
    success = False
    discount = float(discount)
    discount_percent = float(discount) / 100
    has_manager_discount = False
    # Giving way to cookie discount attack
    has_vip_discount = user.is_vip
    if 'user_level' in request.cookies:
        if int(request.cookies['user_level']) == 3:
            has_vip_discount = True
        elif int(request.cookies['user_level']) == 10:
            has_manager_discount = True

    extra_vip_discount = 0
    extra_manager_discount = 0

    if has_vip_discount:
        extra_vip_discount = VIP_DISCOUNT

    if has_manager_discount:
        extra_manager_discount = MANAGER_DISCOUNT

    full_discount = extra_vip_discount + discount_percent + extra_manager_discount

    try:
        desired_food = Food.query.filter_by(id=food_id).one()
        # Applying the discount
        desired_food_price = round(desired_food.price_in_dollars * (1 - full_discount), 1)

        if user.account_balance >= desired_food_price and len(user.order_history) <= USER_MAX_ORDER:
            # Log the food order
            food_order = FoodOrder(food_id=desired_food.id,
                                   user_id=user.id,
                                   price_in_dollars=desired_food_price,
                                   date=parser.parse(request.json['date'].decode('hex')))
            db.session.add(food_order)

            user.account_balance -= desired_food_price
            db.session.commit()
            success = True
            server_message = "The {!s} you ordered is on its way!".format(desired_food.food_name)

            if has_vip_discount:
                server_message += " You got our VIP discount of {!s}%!".format(VIP_DISCOUNT * 100)

            if discount > 0:
                server_message += " You got another " if has_vip_discount else " You got a"
                server_message += " {!s}% discount! ".format(discount_percent * 100)
            server_message += " You paid ${!s}".format(desired_food_price)
        else:
            if len(user.order_history) > USER_MAX_ORDER:
                err_message = ("This might be just a little too much pizza, don't you think?")
            else:
                err_message = ("Your current balance is not sufficient for this order."
                               " Please charge up your account or ask a friend to transfer some credit ")
    except (NoResultFound, MultipleResultsFound), e:
        err_message = "Sorry, could not find the dish you wish to order"
        success = False

    res = dict(success=success,
               server_message=server_message,
               err_message=err_message,
               account_balance=user.account_balance)
    if not inner:
        return jsonify(res)
    else:
        return res


def create_session(user_id):
    key = UserSession.generate_key()
    while UserSession.query.filter_by(key=key).count() > 0:
        key = UserSession.generate_key()

    return UserSession(key=key, user_id=user_id)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    print 'in custom logout'
    ses = UserSession.query.filter_by(key=g.session_key).first()
    db.session.delete(ses)
    db.session.commit()
    resp = redirect(url_for("Home"))
    resp.set_cookie("pizza_session", value='', expires=0)
    return resp


@app.route('/login', methods=['POST'])
def login():
    print 'in custom login'
    user_name = request.form.get("user_name")
    password = request.form.get("password")
    if not password and not user_name:
        return jsonify(dict(success=False, missingAll=True))
    elif not password:
        return jsonify(dict(success=False, missingPassword=True))
    elif not user_name:
        return jsonify(dict(success=False, missingUsername=True))

    print(IS_SQL_INJECTION)

    # print("Is this magshimim project ?  - " + IS_MAGSHIMIM)
    if(not IS_SQL_INJECTION):
        user = User.query.filter_by(user_name=user_name, password=password).first()
    else:
        try:
            sqlLine = 'SELECT * FROM user WHERE user_name="'+user_name+'" AND password="'+password+'"'	
            print(sqlLine)
            users = list(db.session.execute(sqlLine))
            if(len(users) >= 5):
                for oneUser in users:
                    if(oneUser[2] == user_name):
                        user = oneUser
            elif(len(users) > 0):
                user = users[0]
            else:
                user = None
        except:
            user = None

    print(user)

    if not user:
        return jsonify(dict(success=False))

    user_session = create_session(user.id)
    db.session.add(user_session)
    db.session.commit()
    resp = jsonify(dict(success=True))
    resp.set_cookie("pizza_session", value=user_session.key, httponly=False)
    return resp


@app.route('/change', methods=['POST'])
@login_required
def change():
    password = request.form["password"]
    new_password = request.form["newPassword"]

    if new_password == password: 
        return jsonify(dict(success=False, same_password=True))

    if not password or not new_password:
        return jsonify(dict(success=False))

    user = User.query.filter_by(id=g.current_user.id, password=password).first()
    if not user:
        return jsonify(dict(success=False))

    user.password = new_password
    db.session.commit()
    resp = jsonify(dict(success=True))
    return resp


@app.route('/register', methods=['POST'])
def register():
    form = ExtendedRegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=form.password.data,
            user_name=form.user_name.data,
            is_vip=form.is_vip.data
        )
        db.session.add(user)
        db.session.commit()

        to_user_id = user.id
        admin_id = User.query.filter_by(user_name="pizzaluigi").one().id
        message = Message.FromDict(dict(
            from_user_id=admin_id,
            to_user_id=to_user_id,
            subject="Welcome to Pizza Luigi",

            message_text="""Welcome! We're so happy to see you here!<br/><br/>
                             As a new member we invite you to enjoy a pizza with a special offer -
                             <br/><br/>
                             <a href='/?enableSpecial=1'>Get your $5 pizza here!</a>
                             <br/><br/>
                             <small>(Valid for one purchase only)</small>"""
        ))

        db.session.add(message)
        db.session.commit()

        user_session = create_session(to_user_id)

        db.session.add(user_session)
        db.session.commit()

        response = jsonify(dict(success=True))
        response.set_cookie("pizza_session", value=user_session.key, httponly=False)
        return response
    errors = list(chain.from_iterable([form.errors[k] for k in form.errors]))
    return jsonify(dict(success=False, errors=errors))


@app.route('/userinfo/<user_id>', methods=["GET"])
@LogRequestDuration
def GetUserInfo(user_id):
    try:
        received_id = int(user_id)
        data = User.query.filter_by(id=received_id).one()
        return jsonify(dict(email=data.email, username=data.user_name))
    except:
        return jsonify(dict(email="", username=""))


@app.route('/dishes/pizzas/mobile')
@LogRequestDuration
def GetMobilePizzaSelection():
    return jsonify(dict(pizzas=[pizza.ToDict() for pizza in Food.query.filter_by(type=FoodType.SALE).all()]))


@app.route('/dishes/pizzas')
@LogRequestDuration
def GetPizzasSelection():
    return jsonify(dict(pizzas=[pizza.ToDict() for pizza in Food.query.filter_by(type=FoodType.PIZZA).all()]))


@app.route('/dishes/specials')
@LogRequestDuration
def GetSpecialsSelection():
    user = g.current_user
    return jsonify(dict(had_special='YES' if user.had_special else 'NO',
                        specials=[pizza.ToDict() for pizza in Food.query.filter_by(type=FoodType.SPECIAL).all()]))


@app.route('/dishes/sides')
@LogRequestDuration
def GetSidesSelections():
    return jsonify(dict(sides=[pizza.ToDict() for pizza in Food.query.filter_by(type=FoodType.SIDE).all()]))


#################################################
#########      MESSAGES REQUESTS    #############
#################################################

@app.route('/messages/<int:message_id>', methods=['PUT'])
@login_required
@LogRequestDuration
def UpdateUserMessage(message_id):
    print "Fucking here!"
    user = g.current_user
    try:
        message = Message.query.filter_by(id=message_id).one()
        if message.to_user_id == user.id:
            message.unread = json.loads(request.data)['unread']
            db.session.commit()
    except (NoResultFound, MultipleResultsFound), e:
        pass
    return jsonify(dict(unread_messages=len([message for message in user.messages_received if message.unread])))


@app.route('/special')
def specialOrder():
    user_data_dict = GetUserNavBarParams(g.current_user)
    return app.make_response(render_template('specials.html', **user_data_dict))


@app.route('/messages', methods=['GET'], defaults={"requested_message_id": None})
@app.route('/messages/<int:requested_message_id>', methods=['GET'])
@login_required
@LogRequestDuration
def MessageView(requested_message_id):
    user_data_dict = GetUserNavBarParams(g.current_user)
    user = g.current_user
    user_data_dict.update(dict(requested_message=next(
        iter([message.ToDict() for message in user.messages_received if message.id == requested_message_id]), None),
        messages=[message.ToDict() for message in user.messages_received]))
    # For exercise purposes we want to allow sending anew message with a GET
    # so we distinguish between sending a message and getting the user messages
    # by the request parameters
    # For POST, create and send a new message
    if len(request.args) > 0:
        err_message = None
        server_message = None

        try:
            to_user_id = User.query.filter_by(user_name=request.args["to_user"]).one().id
            message = Message.FromDict(dict(
                from_user_id=user.id,
                to_user_id=to_user_id,
                subject=request.args['subject'],
                message_text=request.args['message_text']
            ))

            User.query.filter_by(id=message.to_user_id).one()
            db.session.add(message)
            db.session.commit()
            success = True
            if user.id == to_user_id:
                server_message = "Your message to yourself was sent!"
            else:
                server_message = "Your message was sent to {!s}!".format(message.to_user.user_name)
            
            user_data_dict.update(dict(success=success,
                                       err_message=err_message,
                                       server_message=server_message))
            print("DO THAT!")
            return render_template("inbox.html", **user_data_dict)

        except (NoResultFound, MultipleResultsFound), e:
            err_message = "Sorry, could not find the user you wanted to message"
            success = False

            user_data_dict.update(dict(success=success,
                                       err_message=err_message,
                                       server_message=server_message))

            return render_template("inbox.html", **user_data_dict)

        return redirect(url_for("MessageView"))
    else:
        return render_template("inbox.html", **user_data_dict)


#################################################
#########      STATIC REQUESTS      #############
#################################################

user_regex = '"(((\d+/)?(\w+/)?)+)?"'


@app.route('/<regex({!s}):user_id>change-password-dialog.html'.format(user_regex))
@LogRequestDuration
def GetChangePasswordDialog(user_id):
    user_id = 0
    if g.is_logged_in:
        user_id = g.current_user.id
    return render_template('change-password-dialog.html', csrf_token=generate_csrf(), user_id=user_id)


@app.route('/<regex({!s}):user_id>login-dialog.html'.format(user_regex))
@LogRequestDuration
def GetLoginDialog(user_id):
    return render_template('login-dialog.html', csrf_token=generate_csrf())


@app.route('/<regex({!s}):user_id>register-dialog.html'.format(user_regex))
@LogRequestDuration
def GetRegisterDialogForView(user_id):
    return render_template('register-dialog.html'.format(user_regex), csrf_token=generate_csrf())


@app.route('/<regex({!s}):user_id>transfer-money-dialog.html'.format(user_regex))
@LogRequestDuration
def GetTransferMoneyDialog(user_id):
    return render_template('transfer-money-dialog.html'.format(user_regex))


@app.route('/<regex({!s}):user_id>charge-account-dialog.html'.format(user_regex))
@LogRequestDuration
def GetChargeAccountDialog(user_id):
    return render_template('charge-account-dialog.html'.format(user_regex))


@app.route('/<regex({!s}):user_id>dishes-tabs.html'.format(user_regex))
@LogRequestDuration
def GetDishesTabs(user_id):
    return render_template('dishes-tabs.html'.format(user_regex))


@app.route('/<regex({!s}):user_id>pizzas.html'.format(user_regex))
@LogRequestDuration
def GetPizzaTab(user_id):
    return render_template('pizzas.html'.format(user_regex))


@app.route('/<regex({!s}):user_id>sides.html'.format(user_regex))
@LogRequestDuration
def GetSidesTab(user_id):
    return render_template('sides.html'.format(user_regex))


@app.route('/<regex({!s}):user_id>specials.html'.format(user_regex))
@LogRequestDuration
def GetSpecialsTab(user_id):
    return render_template('specials.html'.format(user_regex))


@app.route('/adminify/admin.html', methods=['GET'])
@LogRequestDuration
def GetAdminPanel():
    status = "DOWN" if is_closed() else "UP"
    return render_template('admin.html',server_status=status)


correct_password = "dbcyberpassword"


@app.route('/adminify/shutdown', methods=['POST'])
@LogRequestDuration
def shutDown():
    password = request.form["password"]
    if password != correct_password:
        return jsonify(dict(success=False))

    if not is_closed():
        with open('lockfile', 'w+') as f:
            f.write("")
    else:
        os.remove('lockfile')

    return jsonify(dict(success=True,blocked=is_closed()))


@app.route('/adminify/restartdb', methods=['POST'])
@LogRequestDuration
def dbrestart():
    try:
        password = request.form["password"]
        if password != correct_password:
            return jsonify(dict(success=False))

        emptyDB()
        init_db()
        return jsonify(dict(success=True))
    except Exception as e:
        return jsonify(dict(success=False,err=e))
    except:
        return "an error has occurred"

@app.route('/adminify/status', methods=['GET'])
@LogRequestDuration
def server_status():
    if is_closed():
        return "DOWN"

    return "UP"


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)

