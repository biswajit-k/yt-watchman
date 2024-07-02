from routes import router
from flask import session, request
from flask_cors import cross_origin
from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib import flow
from utils.utilities import MyException
from youtube.env_details import env_details
from models.user import User
from models.token import Token

from models.db_utils import db_session
from routes.middleware import auth_required

google_request = requests.Request()


@router.route('/api/login', methods=["POST"])
@cross_origin(supports_credentials=True)
def login_user():
    token = request.get_json().get('token')

    try:
        id_info = id_token.verify_oauth2_token(
            token, google_request, env_details['CLIENT_ID'], clock_skew_in_seconds=10)

        session['user_id'] = id_info['sub']
        session.permanent = True

        user = User.get_user(id_info['sub'])
        if user is None:
            print("user dont exits")
            user = User.create_user(id=id_info['sub'], name=id_info['name'], email=id_info['email'])
        return user.asdict()

    except ValueError:
        return {"error": "Opps! Invalid token. Try again."}, 401


@router.route('/api/login/guest', methods=["GET"])
@cross_origin(supports_credentials=True)
def login_guest():
    if 'user_id' in session:
        return {"error": "You are already logged in"}, 405

    guest = User.create_guest_user()
    db_session.add(guest)
    db_session.commit()
    session['user_id'] = guest.id

    return guest.asdict()


@router.route("/api/profile", methods=['GET'])
@cross_origin(supports_credentials=True)
@auth_required
def get_current_user():
    user_id = session.get('user_id')

    user = User.get_user(user_id)

    if not user:
        return {}

    return ({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_guest": user.is_guest(),
        "available_request": user.available_request,
        "has_token": Token.get_token(user.id) is not None,
    })


@router.route("/api/logout", methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
@auth_required
def logout_user():
    user = User.query.filter_by(id=session['user_id']).one()

    if user.is_guest():
        User.delete_guest(user.id)

    session.pop('user_id')
    print("session deleted")
    return {}, 200


@router.route("/api/token_status", methods=['GET'])        # change to something like "request_for_token"
@cross_origin(supports_credentials=True)
@auth_required
def get_token_status():
    user_id = session.get('user_id')
    return Token.get_status(user_id)


@router.route("/api/set_token", methods=['POST'])
@cross_origin(supports_credentials=True)
@auth_required
def set_token_from_code():

    code = request.get_json().get('code')
    if code is None:
        return {"error" :'Code not provided'}, 400

    # create flow
    # TODO: does it work(I have removed openid scope)
    oauth_flow = flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=["https://www.googleapis.com/auth/userinfo.email", "openid",
                "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/youtube.force-ssl"],
        redirect_uri=env_details['WEBSITE_URI'])

    # exchange code with token
    oauth_flow.fetch_token(code=code)

    # set credentials
    credentials = oauth_flow.credentials

    # update db
    user_id = session['user_id']
    existing_token = Token.get_token(user_id)

    if not existing_token:
        token = Token(user_id=user_id, refresh_token=credentials.refresh_token)
        db_session.add(token)
    else:
        existing_token.refresh_token = credentials.refresh_token

    db_session.commit()

    return {"success": "Comment Access Granted!"}


@router.route("/api/comment_access", methods=['GET'])
@cross_origin(supports_credentials=True)
@auth_required
def has_comment_access():

    user_id = session.get('user_id')

    if not Token.get_status(user_id).get('available'):
        return {"status": 0}                            # no comment access

    user_youtube = User.query.filter_by(id=user_id).one().get_youtube()
    if not user_youtube:
        return {"status": 0}                            # no comment access

    try:
        user_channel = user_youtube.get_channel()
    except MyException as e:
        return {"error": str(e)}, 500

    if (len(user_channel["items"]) == 0):
        # comment access, but no user channel to comment
        return {"status": 1}

    # comment access, comment possible
    return {"status": 2}
