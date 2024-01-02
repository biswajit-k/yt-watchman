import humanize
from flask import request, session
from flask_cors import cross_origin

from settings import db
from routes import router
from utils.utilities import format_date, get_duration_seconds
from models.subscription import Subscription, subscriptions_schema
from models.user import User
from youtube.yt_request import youtube
from youtube.youtube import youtube
from routes.middleware import auth_required

# TODO: make routes plural - sub, history routes
@router.route("/api/subscription", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def give_subscriptions():

    user_id = session.get('user_id')
    active_subscription_query = db.session.query(Subscription).filter_by(
        active=True, user_id=user_id).all()
    paused_subscription_query = db.session.query(Subscription).filter_by(
        active=False, user_id=user_id).all()

    user = User.get_user(db.session, user_id)
    total_subscriptions = len(active_subscription_query) + len(paused_subscription_query)
    if (total_subscriptions > user.available_request):
        return {"message": "Oops! requests exceed quota limit"}, 429

    user.available_request -= total_subscriptions

    paused_subscriptions = [subscription.normalize() for subscription
                            in subscriptions_schema.dump(paused_subscription_query)]
    active_subscriptions = [subscription.normalize() for subscription
                            in subscriptions_schema.dump(active_subscription_query)]

    return {"active": active_subscriptions, "paused": paused_subscriptions}
    # try:
    # except:
    #     return {"error": "Opps! something went wrong!"}


@router.route("/api/subscription/stats", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def give_subscriptions_stats():

    user_id = session.get('user_id')
    active_subscriptions = subscriptions_schema.dump(db.session.query(Subscription).filter_by(
        active=True, user_id=user_id).all())
    paused_subscriptions = subscriptions_schema.dump(db.session.query(Subscription).filter_by(
        active=False, user_id=user_id).all())

    auto_comments = 0
    for sub in active_subscriptions + paused_subscriptions:
        if len(sub['comment']) > 0:
            auto_comments += 1

    user = User.get_user(db.session, user_id)
    total_subscriptions = len(active_subscriptions) + paused_subscriptions
    if (total_subscriptions > user.available_request):
        return {"message": "Oops! requests exceed quota limit"}, 429

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
    channel_id = request.json["channelId"]
    tags = request.json["tags"]
    emails = request.json["emails"]
    comment = request.json["comment"]

    if (len(emails) > 5):
        return {"message": "Sorry! maximum 5 emails allowed"}, 400

    subscription_exist = db.session.query(Subscription).filter_by(channel_id=channel_id, user_id=user_id).first()
    if not subscription_exist:
        subscription = Subscription(
            channel_id=channel_id, tags=tags, emails=emails, user_id=user_id, comment=comment)
        db.session.add(subscription)
        db.session.commit()
        return {"message": "Voila! subscription added"}

    return {"message": "Oops! Subscription with same channel already present, try editing it."}, 400


@router.route("/api/subscription/pause/<id>", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def pause_subscriptions(id):
    user_id = session.get('user_id')
    sub = db.session.query(Subscription).filter_by(channel_id=id, user_id=user_id).first()
    sub.active = False
    db.session.commit()
    return {"status": "success"}


@router.route("/api/subscription/resume/<id>", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def resume_subscription(id):
    user_id = session.get('user_id')
    sub = db.session.query(Subscription).filter_by(channel_id=id, user_id=user_id).first()
    sub.active = True
    db.session.commit()
    return {"status": "success"}


@router.route("/api/subscription/delete/<id>", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def delete_subscription(id):
    user_id = session.get('user_id')
    sub = db.session.query(Subscription).filter_by(channel_id=id, user_id=user_id).first()
    db.session.delete(sub)
    db.session.commit()
    return {"status": "success"}


@router.route("/api/subscription/edit/<id>", methods=["POST"])
@cross_origin(supports_credentials=True)
@auth_required
def edit_subscription(id):
    user_id = session.get('user_id')
    sub = db.session.query(Subscription).filter_by(channel_id=id, user_id=user_id).first()
    db.session.delete(sub)
    res = add_subscription()
    return res


@router.route("/api/get_channel", methods=["POST"])
@cross_origin(supports_credentials=True)
@auth_required
def serve_channel():
    url = request.json["url"]
    if (is_channel(url)):
        try:
            channel = youtube.get_channel_from_id(youtube.get_channel_id_from_url(url))
            return channel
        except:
            return {"message": "Something went wrong. please try again"}, 520
    else:
        return {"message": "please enter a valid channel link"}, 400


def is_channel(url):
    import re
    got = re.match(
        r"^https?:\/\/(www\.)?youtube\.com\/(channel\/UC[\w-]{21}[AQgw]|(c\/|user\/|@)?[\w-]+)$", url)
    return got != None
