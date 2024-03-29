import atexit
import inspect
import traceback
from sqlalchemy.orm import scoped_session, sessionmaker

from settings import application, db


def add_app_context(context):

  def middle(func):

    def wrapper(*args, **kwargs):
      context.push()
      return func(*args, **kwargs)

    return wrapper

  return middle

def get_scoped_session():
  with application.app_context():
    session_factory = sessionmaker(bind=db.engine)          # session_factory can create new session according to config provided in sessionmaker constructor
    return scoped_session(session_factory)


"""
uses python decorators to-
creates database session for current function and pass
the session object to it as the first argument.
Also
1. ensures session rollback and termination on abrupt closing of program
2. Rollback changes on exception in function
"""

def create_scoped_session(func):
  # exit handler for handling abrupt closing
  def exit_handler(session):
    if session.is_active:
        print("abort... abrupt closing session!")
        session.rollback()
        session.close()

  def wrapper(*args, **kwargs):
    session_object = get_scoped_session()
    with session_object() as session:
      try:
        # use exit handler
        atexit.unregister(exit_handler)     # remove existing exit handler before registering again
        atexit.register(exit_handler, session=session)

        # assumes that if function with same name is present in the object which is first argument of this function
        # then this function is a method of that object
        if(args and getattr(args[0], func.__name__)):
          method_self, *args = args
          result = func(method_self, session, *args, **kwargs)
        else:
          result = func(session, *args, **kwargs)
        return result

      except Exception:
        print(f"Exception occured\n")
        traceback.print_exc()
        session.rollback()
      finally:
        print("session closing\n")
        session.close()

  return wrapper