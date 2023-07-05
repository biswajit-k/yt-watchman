from flask import session
from functools import wraps


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
      profile = session.get('profile')
      if profile is None:
        return {"error": "Unauthorized"}, 401
      return f(*args, **kwargs)

    return decorated