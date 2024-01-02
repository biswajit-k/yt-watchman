import atexit
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
        atexit.register(exit_handler, session=session)
        result = func(session, *args, **kwargs)
        return result

      except Exception as ex:
        print(f"Exception occured:\n{ex}")
        session.rollback()
      finally:
        print("session closing\n")
        session.close()

  return wrapper
