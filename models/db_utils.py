import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase


db_endpoint = os.environ.get('DB_ENDPOINT')
db_pass = os.environ.get('DB_PASS')
db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')
is_dev = os.environ.get('IS_DEV')

db_uri = "postgresql://postgres:root@localhost:5432/yt-watchman" if is_dev \
            else f"postgresql://{db_user}:{db_pass}@{db_endpoint}:5432/{db_name}"

engine = create_engine(db_uri)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

non_expiring_session = scoped_session(sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine,
                expire_on_commit=False)
            )

class Base(DeclarativeBase):
    query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)

