import random
import string


from models import db
from flask.helpers import url_for

session_size = 20

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(session_size),unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name="session_to_user"))

    @staticmethod
    def generate_key():
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.lowercase) for _ in range(session_size))


