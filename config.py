import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY')
  PERMANENT_SESSION_LIFETIME = timedelta(days=2)
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  STATIC_URL_PATH='/'
  STATIC_FOLDER='./build'
