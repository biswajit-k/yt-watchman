from flask import request, session
from flask_cors import cross_origin

from routes import router
from routes.middleware import auth_required
from models.user import User
from models.db_utils import db_session
from models.subscription import Subscription
from utils.utilities import MyException, get_utc_now


@router.route("/api/subscriptions", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def give_subscriptions():

    user_id = session.get('user_id')
    active_subscription_query = Subscription.query.filter_by(
        active=True, user_id=user_id).all()
    paused_subscription_query = Subscription.query.filter_by(
        active=False, user_id=user_id).all()

    user = User.query.filter_by(id=user_id).one()
    total_subscriptions = len(active_subscription_query) + len(paused_subscription_query)
    if (total_subscriptions > user.available_request):
        return {"error": "Oops! requests exceed quota limit"}, 429

    user.available_request -= total_subscriptions

    try:
        paused_subscriptions = [subscription.normalize() for subscription
                                in paused_subscription_query]
        active_subscriptions = [subscription.normalize() for subscription
                                in active_subscription_query]

        return {"active": active_subscriptions, "paused": paused_subscriptions}
    except MyException as e:
        return {"error": str(e)}, 520

@router.route("/api/subscription/stats", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def give_subscriptions_stats():

    user_id = session.get('user_id')
    active_subscriptions = Subscription.query.filter_by(
        active=True, user_id=user_id).all()
    paused_subscriptions = Subscription.query.filter_by(
        active=False, user_id=user_id).all()

    auto_comments = 0
    for sub in active_subscriptions + paused_subscriptions:
        if len(sub.comment) > 0:
            auto_comments += 1

    user = User.query.filter_by(id=user_id).one()
    total_subscriptions = len(active_subscriptions) + len(paused_subscriptions)
    if (total_subscriptions > user.available_request):
        return {"error": "Oops! requests exceed quota limit"}, 429

    user.available_request -= total_subscriptions
    return {
            "active": len(active_subscriptions),
            "paused": len(paused_subscriptions),
            "auto_comments": auto_comments
        }


@router.route("/api/subscription/add", methods=["POST"])
@cross_origin(supports_credentials=True)
@auth_required
def add_subscription():
    user_id = session.get('user_id')

    data = request.get_json()
    channel_id = data.get("channelId")
    tags = data.get("tags")
    emails = data.get("emails")
    comment = data.get("comment")

    if (len(emails) > 5):
        return {"error": "Sorry! maximum 5 emails allowed"}, 400

    subscription_exist = Subscription.query.filter_by(channel_id=channel_id, user_id=user_id).first()
    if not subscription_exist:
        subscription = Subscription(
            channel_id=channel_id, tags=tags, emails=emails, user_id=user_id, comment=comment, created_at=get_utc_now())
        db_session.add(subscription)
        db_session.commit()
        return {"message": "Voila! subscription added"}

    return {"error": "Oops! Subscription with same channel already present, try editing it."}, 400


@router.route("/api/subscription/pause/<id>", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def pause_subscriptions(id):
    user_id = session.get('user_id')
    sub = Subscription.query.filter_by(channel_id=id, user_id=user_id).one()
    sub.active = False
    db_session.commit()
    return {"status": "success"}


@router.route("/api/subscription/resume/<id>", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def resume_subscription(id):
    user_id = session.get('user_id')
    sub = Subscription.query.filter_by(channel_id=id, user_id=user_id).one()
    sub.active = True
    db_session.commit()
    return {"status": "success"}


@router.route("/api/subscription/delete/<id>", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def delete_subscription(id):
    user_id = session.get('user_id')
    sub = Subscription.query.filter_by(channel_id=id, user_id=user_id).one()
    db_session.delete(sub)
    db_session.commit()
    return {"status": "success"}


@router.route("/api/subscription/edit/<id>", methods=["POST"])
@cross_origin(supports_credentials=True)
@auth_required
def edit_subscription(id):
    user_id = session.get('user_id')
    sub = Subscription.query.filter_by(channel_id=id, user_id=user_id).one()
    db_session.delete(sub)
    db_session.commit()
    res = add_subscription()
    return res


@router.route("/api/get_channel", methods=["POST"])
@cross_origin(supports_credentials=True)
@auth_required
def serve_channel():
    from application import youtube
    url = request.get_json().get("url")
    if (is_channel(url)):
        try:
            channel = youtube.get_channel_from_id(youtube.get_channel_id_from_url(url))
            return channel
        except MyException as e:
            return {"error": str(e)}, 520
        except:
            return {"error": "Something went wrong. please try again"}, 520

    return {"error": "please enter a valid channel link"}, 400


def is_channel(url):
    import re
    got = re.match(
        r"^https?:\/\/(www\.)?youtube\.com\/(channel\/UC[\w-]{21}[AQgw]|(c\/|user\/|@)?[\w-]+)$", url)
    return got != None
