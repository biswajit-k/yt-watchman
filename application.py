from models.token import Token
from models.history import History
from models.subscription import Subscription
from models.user import User
from routes import router
from settings import application, db
from youtube.yt_watchman import YtWatchman

# DB
with application.app_context():
    db.create_all()

# YT_WATCHMAN_CORE
# YtWatchman().start()

# ROUTES
application.register_blueprint(router)
@application.route('/')
def index():
    return application.send_static_file('index.html')

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=80, debug=True)