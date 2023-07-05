from datetime import datetime, timedelta

import humanize
from routes import router
from flask import session, request
from flask_cors import cross_origin
from google.oauth2 import id_token
from google.auth.transport import requests
import google_auth_oauthlib
from settings import db
from youtube.env_details import env_details
from models.user import User, delete_user
from models.token import Token
from youtube.api_util import get_credentials, get_user_channel
from utils.utilities import time_diff

from routes.middleware import auth_required

google_request = requests.Request()


@router.route("/api/authenticate", methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def authenticate():
    profile = session.get('profile')
    is_authenticated = profile is not None
    return {"is_authenticated": is_authenticated}

# TODO: user_details-> make class

@router.route('/api/login', methods=["POST", "GET"])
@cross_origin(supports_credentials=True)
def login_user():
    token = request.json['token']
    id_info = id_token.verify_oauth2_token(
        token, google_request, env_details['CLIENT_ID'])

    session['profile'] = {"id": id_info['sub'], "name": id_info['name'],
                          "email": id_info['email'], "is_guest": False}
    # save_image(id_info['picture'], id_info['sub'])

    user = db.session.query(User).filter_by(id=id_info['sub']).first()
    refresh_request(user)
    if user is None:
        print("user dont exits")
        user = User(id=id_info['sub'],
                    name=id_info['name'], email=id_info['email'])
        db.session.add(user)
        db.session.commit()

    return session['profile']


def refresh_request(user):
    if user is None:
        return
    total_req = (400 if len(user.email) > 0 else 200)
    if (user.available_request < total_req and time_diff(datetime.now(), user.reset_time) >= 86400):
        user.available_request = total_req
        user.reset_time = datetime.now()
    session['profile']['available'] = user.available_request
    session['profile']['reset'] = user.reset_time
    db.session.commit()

@router.route('/api/login/guest', methods=["GET"])
@cross_origin(supports_credentials=True)
def login_guest():

    guest = generate_guest()
    session['profile'] = {"id": guest.id,
                          "name": guest.name, "email": "", "is_guest": True}
    refresh_request(guest)
    return session['profile']


def generate_guest():
    import uuid
    import random
    id = str(uuid.uuid4())
    name = "guest-" + str(random.randrange(10**4, 10**5))
    available_request = 200
    guest = User(id=id, name=name,
                 available_request=available_request, is_guest=True)
    db.session.add(guest)
    db.session.commit()
    print(guest)
    return guest


@router.route("/api/profile", methods=['GET'])
@cross_origin(supports_credentials=True)
def get_current_user():
    profile = session.get('profile')    # set by user
    if not profile:
        return ({"error": "please login"})

    user = db.session.query(User).filter_by(id=profile['id']).first()
    refresh_request(user)
    has_token = get_credentials(profile['id']) is not None
    return ({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_guest": user.is_guest,
        "available_request": user.available_request,
        "has_token": has_token,
    })


@router.route("/api/logout", methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def logout_user():
    profile = session.get('profile')
    if profile is not None:
        if (profile['is_guest'] == True):
            delete_user(profile['id'])
        session.pop('profile')
        print("session deleted")
    return {"message": "success logout"}


@router.route("/api/get_token", methods=['GET'])
@cross_origin(supports_credentials=True)
@auth_required
def get_token():

    profile = session.get('profile')
    if not profile:
        return ({"error": "please login"})
    tok = db.session.query(Token).filter_by(user_id=profile['id']).first()
    if tok is None:
        return {}

    if (tok.available_request > 0 or time_diff(datetime.now(), tok.reset_time) >= 86400):
        return {"available": True}
    return {"reset": humanize.naturaldelta(tok.reset_time + timedelta(days=1) - datetime.now())}


@router.route("/api/set_token", methods=['POST'])
@cross_origin(supports_credentials=True)
@auth_required
def set_token(code=None):

    # create flow
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=["https://www.googleapis.com/auth/userinfo.email", "openid",
                "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/youtube.force-ssl"],
        redirect_uri=env_details['WEBSITE_URI'])

    if code is None:
        code = request.json['code']

    # exchange code with token
    flow.fetch_token(code=code)

    # set credentials
    credentials = flow.credentials

    # update db
    token = Token(user_id=session['profile']['id'],
                  refresh_token=credentials.refresh_token)
    db.session.add(token)
    db.session.commit()

    return {"success": "Comment Access Granted!"}


@router.route("/api/comment_access", methods=['GET'])
@cross_origin(supports_credentials=True)
@auth_required
def has_comment_access():

    profile = session.get('profile')
    if profile is None:
        return {"error": "Oops! Couldn't find credentials. Please login again!"}

    id = session['profile']['id']

    if (get_credentials(id) == None):
        return {"status": 0}                            # no comment access

    user_channel = get_user_channel(id)

    if (len(user_channel["items"]) == 0):
        # comment access, but no user channel to comment
        return {"status": 1}

    # comment access, comment possible
    return {"status": 2}
