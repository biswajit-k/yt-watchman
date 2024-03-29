from datetime import datetime
from sqlalchemy.orm.session import object_session

from models.subscription import Subscription
from settings import db, ma
from utils.utilities import get_utc_now, get_duration_seconds


class History(db.Model):
    video_id = db.Column(db.String(80), primary_key=True, nullable=False)
    user_id = db.Column(db.String(80), primary_key=True, nullable=False)
    channel_id = db.Column(db.String(120), db.ForeignKey('subscription.channel_id'), nullable=False)
    video_title = db.Column(db.String(120), nullable=False)
    tag = db.Column(db.String(120), nullable=False)
    found_at = db.Column(db.DateTime, default=get_utc_now())
    comment_id = db.Column(db.String(120), nullable=False, default='')

    def __repr__(self) -> str:
        return f'''video_id- {self.video_id} \n
        video_title- {self.video_title} \n
        channel_id- {self.channel_id} \n
        tag- {self.tag}  \n
        user_id- {self.user_id}  \n
        comment_id- {self.comment_id}  \n
        found_at- {self.found_at} \n'''

    def get_subscription(self):
        return object_session(self).query(Subscription).filter_by(user_id=self.user_id, channel_id=self.channel_id).first() # type:ignore

    @classmethod
    def normalize(cls, history_dic):
        import copy
        import humanize
        from application import youtube

        history = copy.copy(history_dic)

        video = youtube.get_video(history['video_id'])['items'][0]

        history['imgUrl'] = video['snippet']['thumbnails']['high']['url']
        history['video_title'] = video['snippet']['title']
        history['channel_title'] = video['snippet']['channelTitle']

        time_found = get_duration_seconds(datetime.strptime(history["found_at"], "%Y-%m-%dT%H:%M:%S"))
        if (divmod(time_found, 3600)[0] < 24):
            history["found_at"] = f"Found {humanize.naturaldelta(time_found)} ago"
        else:
            date = datetime.strptime(
                history["found_at"], "%Y-%m-%dT%H:%M:%S")
            history["found_at"] = f"Found on {date.day} {date.strftime('%B')}, {date.year}"
        return history


class HistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = History


history_schema = HistorySchema(many=True)
