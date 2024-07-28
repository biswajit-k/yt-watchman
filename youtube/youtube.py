import os
import traceback
import httplib2
from application import application
from models.db_utils import db_session
from models.token import Token
from models.user import User
from models.user import History
from utils.utilities import MyException, parse_date, upsert
from thread_safe_utils import add_app_context
from youtube.mail_sender import EmailService

class Youtube:

    """
        Youtube(developerKey)

        developer youtube object/class methods:
            *mail_sender()
            *write_file_with_video_extracted


        user youtube object methods:
            user_youtube_credentials(user_id)       - for finding user_channel and making comment
            make_comment(youtube, video_id, comment)


    """
    def __init__(self, youtube):
        self.youtube = youtube

    # TODO: copy exception handling if no channel found from deployed version
    def get_channel_id_from_url(self, url):
        import requests
        import re
        r = requests.get(url)

        if r.status_code == 404:
            raise Exception("Channel not found")

        page_source = r.text
        print(f"channel page response: {r.status_code}")
        channel_id_match = re.search(r"<link\ rel=\"canonical\"\ href=\"https://www\.youtube\.com/channel/(.*?)\"", page_source)

        if channel_id_match is None:
            raise Exception("Unable to get channel Id")

        return channel_id_match.group(1)

class UserYoutube(Youtube):

    def __init__(self, session, user_id):

        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request

        token = Token.get_token(user_id)
        if token:
            cred = UserYoutube.get_credentials(token)
            try:
                cred.refresh(Request())
                youtube = build('youtube', 'v3', credentials=cred)
            except Exception:
                print(f"Exception occured during token refresh - expired maybe\n")
                # traceback.print_exc()
                print("deleting token!")
                session.delete(token)
                youtube = None
        else:
            youtube = None

        self.user_id = user_id
        super().__init__(youtube)

    @classmethod
    def get_credentials(cls, token):
        from google.oauth2 import credentials
        config = {
            'token': None,
            'refresh_token': token.refresh_token,
            'token_uri': 'https://www.googleapis.com/oauth2/v3/token',
            'client_id': os.environ.get('CLIENT_ID'),
            'client_secret': os.environ.get('CLIENT_SECRET')
        }

        return credentials.Credentials(**config)

    def get_channel(self):

        channel_request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        try:
            channel_response = channel_request.execute()
            return channel_response
        except Exception:
            print(traceback.format_exc())
            raise MyException("Network Error! Please try again")

    @add_app_context(application.app_context())
    def handle_comment(self, history, user_id, comment):

        from sqlalchemy.exc import SQLAlchemyError

        user = User.get_user(user_id)

        # lock user_token until the session is committed
        user_token = Token.query.filter_by(user_id=user_id).with_for_update().first()

        if not user or not user_token or not user_token.available_request > 0:
            return
        try:

            # make comment
            self.make_comment(history, comment, user_token)
            print(f"commented for {user_id} here {history.comment_link}")

            # send mail
            EmailService.send_comment_mail(user.email, history)

            # upsert history, since we need to overwrite existing history without comment if present in DB
            history_to_dict = history.to_dict()
            upsert(db_session, History, [history_to_dict])

            # use token
            user_token.available_request -= 1
            db_session.commit()

        except SQLAlchemyError as e:
            print(traceback.format_exc())
            raise e
        except MyException as e:
            print(traceback.format_exc())

    def make_comment(self, history, comment, token):
        request = self.youtube.commentThreads().insert(
            part = "snippet",
            body = {
                "snippet": {
                    "videoId": history.video_id,
                    "topLevelComment": {
                        "snippet": { "textOriginal": comment }
                    }
                }
            }
        )
        try:
            response = request.execute()            # this takes time - TODO: async

            history.comment_id = response['id']
            history.comment = comment
            comment_link = f"https://www.youtube.com/watch?v={history.video_id}&lc={history.comment_id}"
            history.comment_link = comment_link
        except Exception:
            print(traceback.format_exc())
            raise MyException("Network Error at server")

class DeveloperYoutube(Youtube):

    def __init__(self, developer_key):
        from googleapiclient.discovery import build

        youtube = build('youtube', 'v3', developerKey=developer_key)
        super().__init__(youtube)

    def get_channel_from_id(self, channel_id):
        channel_request = self.youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        try:
            channel_response = channel_request.execute(httplib2.Http())

            def human_format(num, round_to=2):
                magnitude = 0
                while abs(num) >= 1000:
                    magnitude += 1
                    num = round(num / 1000.0, round_to)
                return '{:.{}f}{}'.format(num, round_to, ['', 'K', 'M'][magnitude])

            subscribers = human_format(int(channel_response["items"][0]["statistics"]["subscriberCount"]))
            return {
                "title": channel_response["items"][0]["snippet"]["title"],
                "imgUrl": channel_response["items"][0]["snippet"]["thumbnails"]["default"]["url"],
                "subscribers": subscribers,
                "videos": int(channel_response["items"][0]["statistics"]["videoCount"]),
                "id": channel_id,
            }
        except Exception:
            print(traceback.format_exc())
            raise MyException("Network Error! Please try again")

    def get_video(self, video_id):
        video_request = self.youtube.videos().list(
            part="snippet",
            id=video_id
        )
        try:
            video_response = video_request.execute()
            return video_response
        except Exception:
            print(traceback.format_exc())
            raise MyException("Network Error! Please try again")

    def api_activity(self, channel_id):

        activity_request = self.youtube.activities().list(
            part= "snippet,contentDetails",
            channelId= channel_id,
            maxResults = 20
        )
        try:
            activity_response = activity_request.execute()
            return activity_response
        except Exception:
            print(traceback.format_exc())
            raise MyException("Network Error! Please try again")


class Video:

    def __init__(self, id, title, link, time, description, thumbnail_url, channel_title) -> None:
        self.id = id
        self.title = title
        self.link = link
        self.time = time
        self.description = description
        self.thumbnail_url = thumbnail_url
        self.channel_title = channel_title

    def get_matching_tag(self, tags):
        search_text = [word.lower() for word in (self.description.split() + self.title.split())]

        word_match = list(set(tags).intersection(search_text))

        return word_match[0] if len(word_match) > 0 else None

    @classmethod
    def get_latest_videos(cls, youtube, channel_id, last_fetched_video_id):

        response = youtube.api_activity(channel_id)

        result = []
        videos = response["items"]
        latest_video_id = videos[0]['contentDetails']['upload']['videoId'] if len(videos) > 0 else ""

        for video in videos:

            # consider only video upload activities
            if(video["snippet"]["type"] != "upload"):
                continue

            # get publish time in UTC + 0
            publish_time = parse_date(video["snippet"]["publishedAt"][:19])
            video_id = video['contentDetails']['upload']['videoId']

            # stop when already fetched video
            if last_fetched_video_id == "" or (video_id == last_fetched_video_id):
                break

            str_publish_time = publish_time.strftime("%m/%d/%Y, %H:%M:%S")
            title = video["snippet"]["title"]
            description = video["snippet"]["description"]
            video_id = video['contentDetails']['upload']['videoId']
            video_link = "https://www.youtube.com/watch?v=" + video_id
            channel_title = video["snippet"]["channelTitle"]
            thumbnail_url = video["snippet"]["thumbnails"]["medium"]["url"]


            video = Video(id=video_id, title=title, link=video_link, time=str_publish_time,
                          description=description, channel_title=channel_title, thumbnail_url=thumbnail_url)

            result.append(video)

        return result, latest_video_id