from models import db
from flask.helpers import url_for


class FoodType(object):
    PIZZA = 0
    SIDE = 1
    SALE = 2
    SPECIAL = 3

    _VALUES_TO_NAMES = {
        0: "PIZZA",
        1: "SIDE",
        2: "SALE",
        3: "SPECIAL"
    }

    _NAMES_TO_VALUES = {
        "PIZZA": 0,
        "SIDE": 1,
        "SALE": 2,
        "SPECIAL":3
    }


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(100))
    type = db.Column(db.Integer)
    image_url = db.Column(db.String(400))
    price_in_dollars = db.Column(db.Float)

    def ToDict(self):
        return dict(
            id=self.id,
            food_name=self.food_name,
            image_url=url_for('static', filename='images/{!s}'.format(self.image_url)) if self.image_url else None,
            price_in_dollars=self.price_in_dollars
        )


class FoodOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id', name="food_order_food_id_to_food_id"))
    date = db.Column(db.DateTime(400))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name="food_order_user_id_to_user_id"))
    price_in_dollars = db.Column(db.Float)

    food = db.relationship("Food",
                           primaryjoin=food_id==Food.id,
                           uselist=False)

    def ToDict(self):
        return dict(
            id=self.id,
            food_name=self.food.food_name,
            price_in_dollars=self.price_in_dollars,
            date=self.date
        )