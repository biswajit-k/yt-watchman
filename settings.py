import threading
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from youtube.env_details import env_details

#DB CONFIG
db_endpoint = env_details['DB_ENDPOINT']
db_pass = env_details['DB_PASS']
db_name = env_details['DB_NAME']
db_user = env_details['DB_USER']

db_uri = f"mysql+pymysql://{db_user}:{db_pass}@{db_endpoint}:3306/{db_name}"


# static folder not required in dev, as serving frontend seperately
application = Flask("application", static_url_path='/', static_folder='./build')

application.config['SECRET_KEY'] = env_details['SECRET_KEY']
application.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=2)
application.config['SQLALCHEMY_DATABASE_URI'] = db_uri
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(application)


# creates a sqlalchemy object which provides fns. like -
# setting up engine, creating session for each request and closing after, managing connections, etc.
db = SQLAlchemy(application)

# TODO: read about marshmallow requirement in this project- mostly for serialization and i/p validation
ma = Marshmallow(application)