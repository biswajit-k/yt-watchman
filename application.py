from werkzeug.serving import is_running_from_reloader
import threading
from werkzeug.serving import is_running_from_reloader

""" Below models are not used in this file but still imported
    to ensure that the db models are created at the start itself
"""
from models.token import Token
from models.history import History
from models.subscription import Subscription
from models.user import User
from routes import router
from settings import application, db
from youtube.yt_watchman import yt_watchman


# create tables using db models
with application.app_context():
    db.create_all()


# background task
def watchman_runner():
    print('yt-watchman thread started')
    import time
    while True:
        print("running thread")
        yt_watchman()
        time.sleep(20)

"""
    in debug mode ensure that only parent process creates below thread
    prevent reloader process(a side process created for tracking file changes and reload)
    to create duplicate thread
"""
if not is_running_from_reloader():
    YtWatchman = threading.Thread(daemon=True, target=watchman_runner)
    YtWatchman.start()


# ROUTES
application.register_blueprint(router)
@application.route('/')
def index():
    return application.send_static_file('index.html')       # send index.html first then react router will handle any route changes on browser
                                                            # you click button, link changes on browser, router renders component corr. to link

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=80, debug=True)


