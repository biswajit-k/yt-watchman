from datetime import datetime
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from models.db_utils import Base, db_session
from models.token import Token
from models.history import History
from models.subscription import Subscription
from utils.utilities import get_duration_seconds, get_utc_now

LOGGED_IN_USER_QUOTA = 400
GUEST_USER_QUOTA = 200


class User(Base):
    __tablename__ = 'user'
    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(120), default="")
    __reset_time: Mapped[datetime] = mapped_column(default=get_utc_now())
    __available_request: Mapped[int]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__available_request = GUEST_USER_QUOTA if self.is_guest() is True else LOGGED_IN_USER_QUOTA

    def asdict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_guest': self.is_guest()
        }

    def get_youtube(self):
        from youtube.youtube import UserYoutube
        user_youtube = UserYoutube(db_session, self.id)
        return user_youtube if user_youtube.youtube else None

    def is_guest(self):
        return not bool(self.email)

    @property
    def available_request(self):
        request_quota = GUEST_USER_QUOTA if self.is_guest() else LOGGED_IN_USER_QUOTA
        if (get_duration_seconds(self.__reset_time) >= 86400 and self.__available_request < request_quota):
            self.__available_request = request_quota
            self.__reset_time = get_utc_now()
            db_session.commit()           # type: ignore (guaranteed that session exist as object is commited
                                                    #               at the time of creation)

        return self.__available_request

    @available_request.setter
    def available_request(self, value):
        self.__available_request = value
        db_session.commit()            # type: ignore


    @classmethod
    def create_user(cls, id, name, email):
        user = User(id=id, name=name, email=email)
        db_session.add(user)
        db_session.commit()
        return user

    @classmethod
    def get_user(cls, id):
        return User.query.filter_by(id=id).first()

    @classmethod
    def create_guest_user(cls):
        import uuid, random
        id = str(uuid.uuid4())
        name = "guest-" + str(random.randrange(10**2, 10**3))
        guest = User(id=id, name=name)
        db_session.add(guest)
        db_session.commit()
        return guest

    @classmethod
    def delete_guest(cls, user_id):
        Token.query.filter_by(user_id=user_id).delete()
        History.query.filter_by(user_id=user_id).delete()
        Subscription.query.filter_by(user_id=user_id).delete()
        User.query.filter_by(id=user_id).delete()
        db_session.commit()

