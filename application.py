from werkzeug.serving import is_running_from_reloader
import threading
from models.token import Token
from models.history import History
from models.subscription import Subscription
from models.user import User
from routes import router
from settings import application, db
from youtube.yt_watchman import yt_watchman

# DB
with application.app_context():
    db.create_all()

# YT_WATCHMAN_CORE

# TODO: improve logic - remove while 1
def watchman_runner():
    print('yt-watchman thread started')
    import time
    while 1:
        print("running thread")
        # requires app context as thread can't read current application
        yt_watchman(application.app_context())
        time.sleep(20)

# in debug mode flask starts 2 processes, one extra to watch changes and do reload
# so prevent two watchman threads being created, below fn. only runs if this is not the
# reloader process
if not is_running_from_reloader():
    YtWatchman = threading.Thread(daemon=True, target=watchman_runner)
    YtWatchman.start()

# ROUTES
application.register_blueprint(router)
@application.route('/')
def index():
    return application.send_static_file('index.html')

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=True)