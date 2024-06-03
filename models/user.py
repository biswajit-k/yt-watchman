from settings import db
from sqlalchemy.orm.session import object_session

from models.token import Token
from models.history import History
from models.subscription import Subscription
from utils.utilities import get_duration_seconds, get_utc_now

LOGGED_IN_USER_QUOTA = 400
GUEST_USER_QUOTA = 200


class User(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), default="")
    __reset_time = db.Column(db.DateTime, default=get_utc_now())
    __available_request = db.Column(db.Integer, nullable=False)

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
        user_youtube = UserYoutube(object_session(self), self.id)
        return user_youtube if user_youtube.youtube else None

    def is_guest(self):
        return not bool(self.email)

    @property
    def available_request(self):
        request_quota = GUEST_USER_QUOTA if self.is_guest() else LOGGED_IN_USER_QUOTA
        if (get_duration_seconds(self.__reset_time) >= 86400 and self.__available_request < request_quota):
            self.__available_request = request_quota
            self.__reset_time = get_utc_now()
            object_session(self).commit()           # type: ignore (guaranteed that session exist as object is commited
                                                    #               at the time of creation)

        return self.__available_request

    @available_request.setter
    def available_request(self, value):
        self.__available_request = value
        object_session(self).commit()            # type: ignore


    @classmethod
    def create_user(cls, session, id, name, email):
        user = User(id=id, name=name, email=email)
        session.add(user)
        session.commit()
        return user

    @classmethod
    def get_user(cls, session, id):
        return session.query(cls).filter_by(id=id).first()

    @classmethod
    def create_guest_user(cls):
        import uuid, random
        id = str(uuid.uuid4())
        name = "guest-" + str(random.randrange(10**2, 10**3))
        guest = User(id=id, name=name)
        return guest

    @classmethod
    def delete_guest(cls, session, user_id):
        session.query(Token).filter_by(user_id=user_id).delete()
        session.query(History).filter_by(user_id=user_id).delete()
        session.query(Subscription).filter_by(user_id=user_id).delete()
        session.query(cls).filter_by(id=user_id).delete()
        session.commit()

    # user details
    """
        fields:
            public:
                id, name, email, is_guest, token(backref)

            private:
            request(available_request)
        methods:
            classMethods:   # session parameter take
                User.send_mail(cls, session, ...)
                make_comment()
                has_token()
                    user.token.refresh_token is not None and not expired -> change working of get_credentials

            static:
                User.get_user(id)


    """
