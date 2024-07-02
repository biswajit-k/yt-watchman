from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKeyConstraint, String

from models.db_utils import Base, db_session
from models.subscription import Subscription
from utils.utilities import get_utc_now, get_duration_seconds


class History(Base):
    __tablename__ = 'history'
    video_id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    channel_id: Mapped[str] = mapped_column(String(40))
    video_title: Mapped[str] = mapped_column(String(120))
    tag: Mapped[str]
    found_at: Mapped[datetime] = mapped_column(default=get_utc_now())
    comment_id: Mapped[str] = mapped_column(String(120), default='')

    # # non-persistent fields
    # video_link: str
    # thumbnail_url: Mapped[str]
    # channel_title: Mapped[str]
    # video_description: Mapped[str]

    __table_args__ = (ForeignKeyConstraint([user_id, channel_id],
                                           [Subscription.user_id, Subscription.channel_id]), {})


    def __repr__(self) -> str:
        return f'''video_id- {self.video_id} \n
        video_title- {self.video_title} \n
        channel_id- {self.channel_id} \n
        tag- {self.tag}  \n
        user_id- {self.user_id}  \n
        comment_id- {self.comment_id}  \n
        found_at- {self.found_at} \n'''

    def to_dict(self):
        dict = self.__dict__
        dict.pop('_sa_instance_state', None)
        return dict

    def get_subscription(self):
        return Subscription.query.filter_by(user_id=self.user_id, channel_id=self.channel_id).first()

    def normalize(self):
        import humanize
        from application import youtube

        db_session.refresh(self)
        history = self.to_dict()
        video = youtube.get_video(history['video_id'])['items'][0]

        history['imgUrl'] = video['snippet']['thumbnails']['high']['url']
        history['video_title'] = video['snippet']['title']
        history['channel_title'] = video['snippet']['channelTitle']

        time_found = get_duration_seconds(history["found_at"])
        if (divmod(time_found, 3600)[0] < 24):
            history["found_at"] = f"Found {humanize.naturaldelta(time_found)} ago"
        else:
            date = history["found_at"]
            history["found_at"] = f"Found on {date.day} {date.strftime('%B')}, {date.year}"
        return history
