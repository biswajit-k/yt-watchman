from flask import session
from functools import wraps


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
      user_id = session.get('user_id')
      if user_id is None:
        return {"error": "Unauthorized"}, 401
      return f(*args, **kwargs)

    return decorated