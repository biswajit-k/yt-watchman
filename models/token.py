from datetime import datetime
from typing import Any
from sqlalchemy import ForeignKey, String, ForeignKey
from sqlalchemy.orm import object_session, mapped_column, Mapped

from models.db_utils import Base, db_session
from utils.utilities import get_utc_now, get_duration_seconds

# TODO: put constants in a file and import from there like environment variables
TOKEN_QUOTA = 1

class Token(Base):
    __tablename__ = 'token'

    user_id: Mapped[str] = mapped_column(String(120), ForeignKey('user.id'), primary_key=True)
    refresh_token: Mapped[str] = mapped_column(String(120))
    __available_request: Mapped[int] = mapped_column(default=TOKEN_QUOTA)
    __reset_time: Mapped[datetime] = mapped_column(default=get_utc_now())

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
            db_session.commit()   # type: ignore
        return self.__available_request

    @available_request.setter
    def available_request(self, value):
        self.__available_request = value


    # TODO: this function can be made to return time in which comment will get reset
    # 0 - token available; 3352 - 3352 seconds more required; -1 - token not present(use humanize in route, not here)
    @classmethod
    def get_status(cls, user_id):
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

        token = cls.get_token(user_id)
        if token:
            status: dict[str, Any] = {'available': True}
            if token.available_request == 0:
                status['reset'] = humanize.naturaldelta(token.__reset_time + timedelta(days=1) - get_utc_now())
        else:
            status = {'available': False}

        return status

    @classmethod
    def get_token(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()
