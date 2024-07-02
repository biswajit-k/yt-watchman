import humanize
from sqlalchemy import String, ForeignKey
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY

from models.db_utils import Base, db_session
from utils.utilities import get_duration_seconds, get_utc_now

# TODO: delete flaskenv
class Subscription(Base):
    __tablename__ = 'subscription'

    user_id: Mapped[str] = mapped_column(String(40), ForeignKey('user.id'), primary_key=True)
    channel_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String))
    emails: Mapped[list[str]] = mapped_column(ARRAY(String))
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=get_utc_now())
    comment: Mapped[str] = mapped_column(String(240), default='')
    last_video_id_fetched: Mapped[str] = mapped_column(String(50), default='')

    def __repr__(self) -> str:
        return f'''user_id- {self.user_id} \n
        channel_id- {self.channel_id} \n
        emails- {self.emails}\n
        tags- {self.tags}  \n
        active- {self.active} \n
        comment- {self.comment} \n
        last_video_id_fetched- {self.last_video_id_fetched} \n
        created- {self.created_at} \n'''

    def to_dict(self):
        dict = self.__dict__
        dict.pop('_sa_instance_state', None)
        return dict

    def normalize(self):
        from application import youtube

        db_session.refresh(self)        # TODO: sqlalchemy is not mapping list objects(obj.property raises error), so I refreshed explicitly
        subscription = self.to_dict()
        channel = youtube.get_channel_from_id(subscription["channel_id"])
        time_found = get_duration_seconds(subscription["created_at"])
        if (divmod(time_found, 3600)[0] < 24):
            subscription["created_at"] = f"Created {humanize.naturaldelta(time_found)} ago"
        else:
            date = subscription["created_at"]
            subscription["created_at"] = f"Created on {date.day} {date.strftime('%B')}, {date.year}"

        subscription["title"] = channel["title"]
        subscription["imgUrl"] = channel["imgUrl"]

        return subscription

