from models import db


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unread = db.Column(db.Boolean, default=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id', name="message_from_user_id_user_id"))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id', name="message_to_user_id_user_id"))
    subject = db.Column(db.String(400))
    message_text = db.Column(db.String(400))

    def ToDict(self):
        return dict(
            id=self.id,
            from_user=self.from_user.user_name,
            to_user=self.to_user.user_name,
            message_text=self.message_text,
            subject=self.subject,
            unread=self.unread
        )

    @staticmethod
    def FromDict(message_dict):
        return Message(**message_dict)