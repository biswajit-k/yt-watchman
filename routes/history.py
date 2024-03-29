from flask import session
from flask_cors import cross_origin

from settings import db
from routes import router
from models.history import History, history_schema
from models.user import User

from routes.middleware import auth_required


@router.route("/api/history", methods=["GET"])
@cross_origin(supports_credentials=True)
@auth_required
def give_history():
    user_id = session.get('user_id')
    history_query = db.session.query(History).filter_by(user_id=user_id).all()

    user = User.get_user(db.session, user_id)
    if (len(history_query) > user.available_request):
        return {"message": "Oops! requests exceed quota limit"}, 429

    user.available_request -= len(history_query)
    history_list = [history.normalize() for history in history_schema.dump(history_query)]
    return {"history": history_list}

