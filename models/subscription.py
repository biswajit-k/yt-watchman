from datetime import datetime
from settings import db, ma
from utils.utilities import get_utc_now


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), db.ForeignKey('user.id'),
                        nullable=False)
    # user = db.relationship('User',                                  # User table has a backref named 'subscription' in subscription table
    #                        backref='subscriptions', lazy=True)                         # subscription table call it as 'user'
    channel_id = db.Column(db.String(80), nullable=False)
    tags = db.Column(db.JSON, nullable=False)
    emails = db.Column(db.JSON, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=get_utc_now())
    comment = db.Column(db.String(240), nullable=False, default='')
    last_fetched_at = db.Column(
        db.DateTime, nullable=False, default=get_utc_now())

    def __repr__(self) -> str:
        return f'''sub_id- {self.id} \n
        user_id- {self.user_id} \n
        channel_id- {self.channel_id} \n
        emails- {self.emails}\n
        tags- {self.tags}  \n
        active- {self.active} \n
        comment- {self.comment} \n
        last_fetched_at- {self.last_fetched_at} \n
        created- {self.created_at} \n'''


class SubscriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Subscription


subscriptions_schema = SubscriptionSchema(many=True)


def delete_subscription(user_id):
    subscriptions = db.session.query(
        Subscription).filter_by(user_id=user_id).delete()
    db.session.commit()
