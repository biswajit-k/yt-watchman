from flask import Blueprint
router = Blueprint('router', __name__)

from routes import middleware, oauth, subscription, history