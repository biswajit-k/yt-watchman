from datetime import datetime
from settings import db, ma
from utils.utilities import get_utc_now

from models.history import delete_history
from models.subscription import delete_subscription
from models.token import delete_token


class User(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), default="")
    available_request = db.Column(db.Integer, default=400)
    reset_time = db.Column(db.DateTime, default=get_utc_now())
    is_guest = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"{self.id}  {self.name} {self.email}"


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


uses_schema = UserSchema(many=True)


def delete_user(id):
    delete_subscription(id)
    delete_history(id)
    delete_token(id)

    user = db.session.query(User).filter_by(id=id).delete()
    db.session.commit()
