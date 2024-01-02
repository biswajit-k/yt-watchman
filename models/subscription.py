import humanize
from settings import db, ma
from utils.utilities import format_date, get_duration_seconds, get_utc_now
from youtube.youtube import youtube

# TODO: If I have backref to user then I don't need user_id column
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

    def normalize(self):        # TODO: check if subscription_schema.dump can implement this functionaligy
        import copy

        subscription = copy.copy(self)

        channel = youtube.get_channel_from_id(subscription["channel_id"])
        time_found = get_duration_seconds(format_date(subscription["created_at"]))
        if (divmod(time_found, 3600)[0] < 24):
            subscription["created_at"] = f"Created {humanize.naturaldelta(time_found)} ago"
        else:
            date = format_date(subscription["created_at"])
            subscription["created_at"] = f"Created on {date.day} {date.strftime('%B')}, {date.year}"

        subscription["title"] = channel["title"]
        subscription["imgUrl"] = channel["imgUrl"]

        return subscription

    """
        fields:
            public:
                sub_id, channel_id, *channel_title, tags, emails, active, comment
        methods:
            public:

            static:
                Subscription.get_sub(channel_id, user_id)
                Subscription.fetch_videos(channel_id, last_fetch_time)
                    return videos, fetched_time, update all channels fetch_time - see extract_video in api_util
    """


class SubscriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Subscription


subscriptions_schema = SubscriptionSchema(many=True)
