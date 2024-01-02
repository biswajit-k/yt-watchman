from settings import db, ma
from sqlalchemy.orm.session import object_session

from models.token import Token
from models.history import History
from models.subscription import Subscription
from youtube.youtube import UserYoutube
from utils.utilities import get_duration_seconds, get_utc_now
from youtube.env_details import env_details
from youtube.mail_sender import send_mail

LOGGED_IN_USER_QUOTA = 400
GUEST_USER_QUOTA = 200

SENDER_EMAIL = env_details['SENDER_EMAIL']
SENDER_PASS = env_details['SENDER_PASS']


class User(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), default="")
    __reset_time = db.Column(db.DateTime, default=get_utc_now())
    __available_request = db.Column(db.Integer, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__available_request = GUEST_USER_QUOTA if kwargs.get('is_guest') is True else LOGGED_IN_USER_QUOTA

    def __repr__(self):
        return f"{self.id}  {self.name} {self.email}"

    def asdict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_guest': self.is_guest
        }

    def get_youtube(self):
        return self.has_token and UserYoutube(object_session(self), self.id) or None

    def send_history_mail(self, history):
        subject = "Youtube Watchman | Comment made on video sucessfully!"
        body = f"""Hi Subscriber,\n\n
                   Comment made on your behalf on video. The details are below-
                   Title: {history.video_title}\n
                   Tag Found: {history.tag}\n
                   Comment Link: https://www.youtube.com/watch?v={history.video_id}&lc={history.comment_id}\n\n

                   Relax and let watchman work for you.\n
                   YT-Watchman
                """
        send_mail(SENDER_EMAIL, SENDER_PASS, self.email, subject, body)



    @property
    def is_guest(self):
        return self.email == ''

    @property
    def available_request(self):
        request_quota = LOGGED_IN_USER_QUOTA if self.is_guest else GUEST_USER_QUOTA
        if (get_duration_seconds(self.__reset_time) >= 86400 and self.__available_request < request_quota):
            self.__available_request = request_quota
            self.__reset_time = get_utc_now()
            object_session(self).commit()
        return self.__available_request

    @available_request.setter
    def available_request(self, value):
        self.__available_request = value
        object_session(self).commit()

    @property
    def has_token(self):
        return Token.get_credentials(object_session(self), self.id) is not None

    @classmethod
    def get_user(cls, session, id):
        return session.query(cls).filter_by(id=id).first()

    @classmethod
    def create_guest_user(cls):
        import uuid, random
        id = str(uuid.uuid4())
        name = "guest-" + str(random.randrange(10**4, 10**5))
        guest = User(id=id, name=name, is_guest=True)
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


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


users_schema = UserSchema(many=True)        # TODO: not used anywhere
