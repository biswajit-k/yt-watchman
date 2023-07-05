import humanize
from datetime import datetime
from flask import session
from flask_cors import cross_origin

from settings import db
from routes import router
from models.history import History, history_schema
from models.user import User
from youtube.api_util import get_video
from youtube.yt_request import youtube

from routes.middleware import auth_required


@router.route("/api/history", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def give_history():
    user_id = session.get('profile').get('id')
    history_query = db.session.query(History).filter_by(user_id=user_id).all()

    user = db.session.query(User).filter_by(id=user_id).first()
    if (len(history_query) > user.available_request):
        return {"error": "Oops! requests exceed quota limit"}

    user.available_request -= len(history_query)
    db.session.commit()
    history_list = normalize_history(history_schema.dump(history_query))
    return {"history": history_list}


def normalize_history(history_list):
    for history in history_list:
        video = get_video(youtube, history['video_id'])['items'][0]
        history['imgUrl'] = video['snippet']['thumbnails']['high']['url']
        history['title'] = video['snippet']['title']
        history['channel_title'] = video['snippet']['channelTitle']

        time_diff = datetime.now() - \
            datetime.strptime(history["found_at"], "%Y-%m-%dT%H:%M:%S.%f")
        if (divmod(time_diff.total_seconds(), 3600)[0] < 24):
            history["found_at"] = f"Found {humanize.naturaldelta(time_diff)} ago"
        else:
            date = datetime.strptime(
                history["found_at"], "%Y-%m-%dT%H:%M:%S.%f")
            history["found_at"] = f"Found on {date.day} {date.strftime('%B')}, {date.year}"

    return history_list
