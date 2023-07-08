import threading
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_session import Session
from youtube.env_details import env_details

#DB CONFIG

if env_details['IS_DEV']:
    db_uri = 'mysql+pymysql://root:@localhost/yt-watchman'
else:
    db_endpoint = env_details['DB_ENDPOINT']
    db_pass = env_details['DB_PASS']
    db_name = env_details['DB_NAME']
    db_user = env_details['DB_USER']
    db_uri = f"mysql+pymysql://{db_user}:{db_pass}@{db_endpoint}:3306/{db_name}"



# OVERRIDE FLASK - allow multithreading to run when application initializes
POOL_TIME = 5
yourThread = threading.Thread()

application = Flask("application", static_url_path='/', static_folder='./build')

application.config['SECRET_KEY'] = env_details['APP_CONFIG_SECRET']
application.config['SQLALCHEMY_DATABASE_URI'] = db_uri
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SESSION_TYPE'] = 'sqlalchemy'
CORS(application)


# creates a sqlalchemy object which provides fns. like -
# setting up engine, creating session for each request and closing after, managing connections, etc.
db = SQLAlchemy(application)

with application.app_context():
    session_factory = sessionmaker(bind=db.engine)
    Db_scoped_session = scoped_session(session_factory)


# TODO: read about marshmallow requirement in this project- mostly for serialization and i/p validation
ma = Marshmallow(application)
application.config['SESSION_SQLALCHEMY'] = db


# TODO: optimize sessions part
sess = Session(application)