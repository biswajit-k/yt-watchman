from flask import Flask
from flask_cors import CORS
from werkzeug.serving import is_running_from_reloader
import threading
import os

""" Below models are not used in this file but still imported
    to ensure that the db models are created at the start itself
"""
from config import Config
from models.db_utils import init_db, db_session
from routes import router


def init_app(config_class=Config):
    application = Flask(
                        import_name="application",
                        static_url_path=config_class.STATIC_URL_PATH,
                        static_folder=config_class.STATIC_FOLDER
                    )
    application.config.from_object(config_class)
    init_db()
    CORS(application)

    return application


application = init_app()

# remove the scoped_session on app close
@application.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# ROUTES
application.register_blueprint(router)

@application.route('/')
def index():
    # send index.html first then react router will handle any route changes on browser
    # you click button, link changes on browser, router renders component corr. to link
    return application.send_static_file('index.html')

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=80, debug=True)


#####################################################################################################
# Initialize other objects/services
from youtube.youtube import DeveloperYoutube
youtube = DeveloperYoutube(developer_key=os.environ.get('YT_API_KEY'))


#####################################################################################################
# Background Thread
from youtube.yt_watchman import yt_watchman

def watchman_runner():

    print('yt-watchman thread started')
    import time
    while True:
        print("running thread")
        yt_watchman()  # type: ignore
        time.sleep(5)

"""
    in debug mode ensure that only parent process creates below thread
    prevent reloader process(a side process created for tracking file
    changes and reload) to create duplicate thread
"""
if not is_running_from_reloader():
    threading.Thread(daemon=True, target=watchman_runner).start()


