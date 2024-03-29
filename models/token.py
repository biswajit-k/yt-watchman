import os
from sqlalchemy.orm.session import object_session

from settings import db, ma
from utils.utilities import get_utc_now, get_duration_seconds

# TODO: put constants in a file and import from there like environment variables
TOKEN_QUOTA = 1

class Token(db.Model):
    user_id = db.Column(db.String(120), db.ForeignKey('user.id'), primary_key=True)
    refresh_token = db.Column(db.String(120), nullable=False)
    __available_request = db.Column(db.Integer, default=TOKEN_QUOTA)
    __reset_time = db.Column(db.DateTime, default=get_utc_now())

    def __repr__(self) -> str:
        return f'''user_id- {self.user_id} \n
      refresh_token- {self.refresh_token} \n
      reset_time- {self.__reset_time} \n
      available_request- {self.__available_request} \n'''


    @property
    def available_request(self):
        if (get_duration_seconds(self.__reset_time) >= 86400 and self.__available_request == 0):
            self.__available_request = TOKEN_QUOTA
            self.__reset_time = get_utc_now()
            object_session(self).commit()   # type: ignore
        return self.__available_request

    @available_request.setter
    def available_request(self, value):
        self.__available_request = value


    def get_credentials(self, refresh=False):
        """ returns credentials if token is valid else deletes it and returns None
        """
        from google.oauth2 import credentials
        from google.auth.transport.requests import Request

        config = {
            'token': None,
            'refresh_token': self.refresh_token,
            'token_uri': 'https://www.googleapis.com/oauth2/v3/token',
            'client_id': os.environ.get('CLIENT_ID'),
            'client_secret': os.environ.get('CLIENT_SECRET')
        }

        cred = credentials.Credentials(**config)

        if cred.expired:
            print("token is expired")
            object_session(self).delete(self)       # type:ignore
            return None

        if refresh:
            cred.refresh(Request())

        return cred

    # TODO: this function can be made to return time in which comment will get reset
    # 0 - token available; 3352 - 3352 seconds more required; -1 - token not present(use humanize in route, not here)
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

        token = cls.get_token(session, user_id)
        status = {
            'available': (token and token.get_credentials() is not None) or False
        }
        if status.get('available'):
            if token.available_request == 0:
                status['reset'] = humanize.naturaldelta(token.__reset_time + timedelta(days=1) - get_utc_now())  # type: ignore

        return status

    @classmethod
    def get_token(cls, session, user_id):
        return session.query(cls).filter_by(user_id=user_id).first()
