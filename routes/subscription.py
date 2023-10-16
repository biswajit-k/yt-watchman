import humanize
from datetime import datetime
from flask import request, session
from flask_cors import cross_origin

from settings import db
from routes import router
from utils.utilities import format_date, get_utc_now
from models.subscription import Subscription, subscriptions_schema
from models.user import User
from youtube.yt_request import youtube, make_comment
from youtube.api_util import get_channel_from_id, get_channel_id_from_url, get_youtube
from routes.middleware import auth_required


@router.route("/api/subscription", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def give_subscriptions():

    user_id = session.get('profile').get('id')
    active_sub_query = db.session.query(Subscription).filter_by(
        active=True, user_id=user_id).all()
    paused_sub_query = db.session.query(Subscription).filter_by(
        active=False, user_id=user_id).all()

    user = db.session.query(User).filter_by(id=user_id).first()
    if (len(active_sub_query) + len(paused_sub_query) > user.available_request):
        return {"error": "Oops! requests exceed quota limit"}

    user.available_request -= len(active_sub_query) + len(paused_sub_query)
    db.session.commit()

    paused_sub = normalize_subs(subscriptions_schema.dump(paused_sub_query))
    active_sub = normalize_subs(subscriptions_schema.dump(active_sub_query))

    return {"active": active_sub, "paused": paused_sub}
    # try:
    # except:
    #     return {"error": "Opps! something went wrong!"}


def str_to_list(s):
    # replace(" ' ") means for "['hi', 'there']"
    return [i.strip() for i in s[1:-1].replace("'", "").split(',')]


def normalize_subs(subs):
    for sub in subs:
        channel = get_channel_from_id(youtube, sub["channel_id"])
        time_diff = get_utc_now() - format_date(sub["created_at"])
        if (divmod(time_diff.total_seconds(), 3600)[0] < 24):
            sub["created_at"] = f"Created {humanize.naturaldelta(time_diff)} ago"
        else:
            date = format_date(sub["created_at"])
            sub["created_at"] = f"Created on {date.day} {date.strftime('%B')}, {date.year}"

        sub["title"] = channel["title"]
        sub["imgUrl"] = channel["imgUrl"]
    return subs

@router.route("/api/subscription/stats", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def give_subscriptions_stats():

    user_id = session.get('profile').get('id')
    active_sub = subscriptions_schema.dump(db.session.query(Subscription).filter_by(
        active=True, user_id=user_id).all())
    paused_sub = subscriptions_schema.dump(db.session.query(Subscription).filter_by(
        active=False, user_id=user_id).all())

    auto_comments = 0
    for sub in active_sub + paused_sub:
        if len(sub['comment']) > 0:
            auto_comments += 1

    user = db.session.query(User).filter_by(id=user_id).first()
    if (len(active_sub) + len(paused_sub) > user.available_request):
        return {"error": "Oops! requests exceed quota limit"}

    user.available_request -= len(active_sub) + len(paused_sub)
    db.session.commit()
    print(auto_comments)
    return {"active": len(active_sub), "paused": len(paused_sub), "auto_comments": auto_comments}


@router.route("/api/subscription/add", methods=["POST"])
@cross_origin(supports_credentials=True)
@auth_required
def add_subscription():
    user_id = session.get('profile').get('id')
    channel_id = request.json["channelId"]
    tags = request.json["tags"]
    emails = request.json["emails"]
    comment = request.json["comment"]
    print(f"-------------{comment}")
    if (len(emails) > 5):
        return {"error": "Sorry! maximum 5 emails allowed"}

    subscription_exist = db.session.query(Subscription).filter_by(
        channel_id=channel_id, user_id=user_id).first()
    if (subscription_exist is None):
        subscription = Subscription(
            channel_id=channel_id, tags=tags, emails=emails, user_id=user_id, comment=comment, created_at=get_utc_now())
        db.session.add(subscription)
        db.session.commit()
        return {"message": "Voila! subscription added"}

    return {"error": "Oops! Subscription with same channel already present, try editing it."}
    # try:
    # except:
    #     return {"error": "Opps! something went wrong. Try again!"}


@router.route("/api/subscription/pause/<id>", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def pause_subscriptions(id):
    user_id = session.get('profile').get('id')
    sub = db.session.query(Subscription).filter_by(
        channel_id=id, user_id=user_id).first()
    sub.active = False
    db.session.commit()
    return {"status": "success"}


@router.route("/api/subscription/resume/<id>", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def resume_subscription(id):
    user_id = session.get('profile').get('id')
    sub = db.session.query(Subscription).filter_by(
        channel_id=id, user_id=user_id).first()
    sub.active = True
    db.session.commit()
    return {"status": "success"}


@router.route("/api/subscription/delete/<id>", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def delete_subscription(id):
    user_id = session.get('profile').get('id')
    sub = db.session.query(Subscription).filter_by(
        channel_id=id, user_id=user_id).first()
    db.session.delete(sub)
    db.session.commit()
    return {"status": "success"}


@router.route("/api/subscription/edit/<id>", methods=["POST"])
@cross_origin(supports_credentials=True)
@auth_required
def edit_subscription(id):
    user_id = session.get('profile').get('id')
    sub = db.session.query(Subscription).filter_by(
        channel_id=id, user_id=user_id).first()
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
            channel = get_channel_from_id(
                youtube, get_channel_id_from_url(url))
            return channel
        except Exception as e:
            return {"error": str(e) or "Something went wrong. please try again"}
    else:
        return {"error": "please enter a valid channel link"}


def is_channel(url):
    import re
    got = re.match(
        r"^https?:\/\/(www\.)?youtube\.com\/(channel\/UC[\w-]{21}[AQgw]|(c\/|user\/|@)?[\w-]+)$", url)
    return got != None
