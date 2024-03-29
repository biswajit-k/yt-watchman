import logging
from models.token import Token
from models.user import User
from settings import application
from utils.utilities import format_date
from thread_safe_utils import add_app_context, create_scoped_session

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
        from models.token import Token

        token = Token.get_token(session, user_id)
        if not Token:
            return None

        user_credentials = token.get_credentials(refresh=True)
        youtube = build('youtube', 'v3', credentials=user_credentials)
        super().__init__(youtube)

    def get_channel(self):
        if self.youtube is None:
            return None

        channel_request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        channel_response = channel_request.execute()
        return channel_response


    @add_app_context(application.app_context())
    @create_scoped_session
    def make_comment(self, session, history, user_id, comment, user_lock):

        from sqlalchemy.exc import SQLAlchemyError

        user = User.get_user(session, user_id)
        user_token = Token.get_token(session, user.id)

        if not user or not user_token:
            return
        try:
            request = self.youtube.commentThreads().insert(
                part="snippet",
                body={
                "snippet": {
                    "videoId": history.video_id,
                    "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment
                    }
                    }
                }
                }
            )
            response = request.execute()
            history.comment_id = response['id']
            print(f"commented for {user_id} here https://www.youtube.com/watch?v={history.video_id}&lc={history.comment_id}")
            # send mail
            user.send_commented_mail(history)
            # add to history
            session.add(history)
            # use token
            user_token.available_request -= 1
            session.commit()

        except SQLAlchemyError as e:
            logging.error("Object deleted but trying to access")
            raise e
        finally:
            user_lock.release()
            print("lock released")


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
        channel_response = channel_request.execute()

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

    def get_video(self, video_id):
        video_request = self.youtube.videos().list(
            part="snippet",
            id=video_id
        )
        video_response = video_request.execute()
        return video_response

    def api_activity(self, channel_id):

        activity_request = self.youtube.activities().list(
            part= "snippet,contentDetails",
            channelId= channel_id,
            maxResults = 20
        )
        activity_response = activity_request.execute()
        return activity_response


    # def extract_video(self, channel_id, tag_list, last_fetch_time):

class Video:

    def __init__(self, id, title, link, time, description) -> None:
        self.id = id
        self.title = title
        self.link = link
        self.time = time
        self.description = description

    def get_matching_tag(self, tags):
        search_text = [word.lower() for word in (self.description.split() + self.title.split())]

        word_match = list(set(tags).intersection(search_text))

        return word_match[0] if len(word_match) > 0 else None

    @classmethod
    def get_latest_videos(cls, youtube, channel_id, last_fetch_time):
        from utils.utilities import get_utc_now

        response = youtube.api_activity(channel_id)

        result = []
        current_time = get_utc_now()

        for video in response["items"]:

            # ignore playlistItem
            if(video["snippet"]["type"] != "upload"):
                continue

            # get publish time in UTC + 0
            publish_time = format_date(video["snippet"]["publishedAt"][:19])

            # stop when already fetched video
            if(publish_time <= last_fetch_time):
                break

            str_publish_time = publish_time.strftime("%m/%d/%Y, %H:%M:%S")
            title = video["snippet"]["title"]
            description = video["snippet"]["description"]
            video_id = video['contentDetails']['upload']['videoId']
            video_link = "https://www.youtube.com/watch?v=" + video_id

            video = Video(id=video_id, title=title, link=video_link, time=str_publish_time, description=description)

            result.append(video)

        return result, current_time