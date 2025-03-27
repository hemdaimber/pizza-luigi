from sqlalchemy.orm import backref
from models import db
from flask_security import UserMixin, RoleMixin
from models.food import FoodOrder
from models.message import Message


roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    user_name = db.Column(db.String(255), unique=True)
    is_vip = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(255))
    account_balance = db.Column(db.Integer, default=0)
    had_special = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    messages_received = db.relationship('Message',
                                        primaryjoin=id==Message.to_user_id,
                                        uselist=True,
                                        backref=backref('to_user'))
    messages_sent = db.relationship('Message',
                                    primaryjoin=id==Message.from_user_id,
                                    uselist=True,
                                    backref=backref('from_user'))

    order_history = db.relationship('FoodOrder',
                                    primaryjoin=id==FoodOrder.user_id,
                                    uselist=True,
                                    backref=backref('user'))