from sqlalchemy.orm.session import object_session

from settings import db, ma
from utils.utilities import get_utc_now, get_duration_seconds
from youtube.env_details import env_details

TOKEN_QUOTA = 1

class Token(db.Model):
    user_id = db.Column(db.String(120), db.ForeignKey('user.id'),
                        primary_key=True)
    refresh_token = db.Column(db.String(120), nullable=False)
    __available_request = db.Column(db.Integer, default=TOKEN_QUOTA)
    __reset_time = db.Column(db.DateTime, default=get_utc_now())

    def __repr__(self) -> str:
        return f'''user_id- {self.user_id} \n
      refresh_token- {self.refresh_token} \n
      reset_time- {self.reset_time} \n
      available_request- {self.available_request} \n'''


    @property
    def available_request(self):
        if (get_duration_seconds(self.__reset_time) >= 86400 and self.__available_request == 0):
            self.__available_request = TOKEN_QUOTA
            self.__reset_time = get_utc_now()
            object_session(self).commit()
        return self.__available_request

    @available_request.setter
    def available_request(self, value):
        self.__available_request = value


    @classmethod
    def get_status(cls, session, user_id):
        """
        returns object with either of below property-
        available:
            True: token available
            False: token not created or not valid
        reset:
            When {'available': True} and request_available == 0
            value is string representing cooldown time
        """
        import humanize
        from datetime import timedelta

        token = session.query(cls).filter_by(user_id=user_id).first()
        status = {
            'available': token is not None
        }
        if status.get('available'):
            if token.available_request == 0:
                status['reset'] = humanize.naturaldelta(token.__reset_time + timedelta(days=1) - get_utc_now())

        return status

    @classmethod
    def get_token(cls, session, user_id):
        return session.query(cls).filter_by(user_id=user_id).first()

    @classmethod
    def get_credentials(cls, session, user_id):                # checks if token present and is valid else deletes it
        token = cls.get_token(session, user_id)

        client_id = env_details['CLIENT_ID']
        client_secret = env_details['CLIENT_SECRET']
        access_token = cls.fetch_access_token(client_id, client_secret, token.refresh_token) if token else None

        if token and not access_token:
            token.delete()
            session.commit()

        return access_token and {
            'token': access_token,
            'refresh_token': token.refresh_token,
            'token_uri': 'https://www.googleapis.com/oauth2/v3/token',
            'client_id': env_details['CLIENT_ID'],
            'client_secret': env_details['CLIENT_SECRET'],
        }

    @classmethod
    def fetch_access_token(cls, client_id, client_secret, refresh_token):
        import requests

        params = {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token
        }

        authorization_url = "https://oauth2.googleapis.com/token"

        r = requests.post(authorization_url, data=params)

        if r.ok:
                return r.json()['access_token']
        else:
                return None


    """
        fields:
            public:
                token.user_id
                token.refresh_token
            private:
                token.count
                token.reset_time
        methods:
            token.is_available()
                yes, if present or (cooldown > 1 day: update to 1 in this case)
            token.use()
                check if available, else raise exception
                subsctract, and update reset_time
    """



class TokenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Token


token_schema = TokenSchema()
