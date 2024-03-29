from werkzeug.serving import is_running_from_reloader
import threading
import os

""" Below models are not used in this file but still imported
    to ensure that the db models are created at the start itself
"""
from settings import application, db
from models.token import Token
from models.history import History
from models.subscription import Subscription
from models.user import User
from routes import router
from youtube.yt_watchman import yt_watchman
from youtube.youtube import DeveloperYoutube

# create tables using db models
with application.app_context():
    db.create_all()

youtube = DeveloperYoutube(developer_key=os.environ.get('YT_API_KEY'))

# background task - I am keeping this thread alive, I can start new thread after every 5s instead to free resources
def watchman_runner():
    print('yt-watchman thread started')
    import time
    while True:
        print("running thread")
        yt_watchman()  # type: ignore
        time.sleep(5)

"""
    in debug mode ensure that only parent process creates below thread
    prevent reloader process(a side process created for tracking file changes and reload)
    to create duplicate thread
"""
if not is_running_from_reloader():
    threading.Thread(daemon=True, target=watchman_runner).start()

# ROUTES
application.register_blueprint(router)

@application.route('/')
def index():
    return application.send_static_file('index.html')       # send index.html first then react router will handle any route changes on browser
                                                            # you click button, link changes on browser, router renders component corr. to link

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=80, debug=True)


