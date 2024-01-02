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
        self.__youtube = youtube

    # TODO: copy exception handling if no channel found from deployed version
    def get_channel_id_from_url(url):
        import requests
        import re
        r = requests.get(url)
        # print(r.status_code)
        # print("get channelId error- " + r.raise_for_status())
        page_source = r.text
        channel_id = re.search(r"<link\ rel=\"canonical\"\ href=\"https://www\.youtube\.com/channel/(.*?)\"", page_source).group(1)
        return channel_id


class UserYoutube(Youtube):

    def __init__(self, session, user_id):
        from google.oauth2 import credentials
        import googleapiclient
        from models.token import Token

        user_credentials = credentials.Credentials(**(Token.get_credentials(session, user_id)))
        youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=user_credentials)
        super().__init__(youtube)

    def get_channel(self):
        if self.__youtube is None:
            return None

        channel_request = self.__youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        channel_response = channel_request.execute()
        return channel_response

    def make_comment(self, session, history, user, comment, user_token):
        request = self.__youtube.commentThreads().insert(
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

        # send mail
        user.send_history_mail(history)
        # add to history
        session.add(history)
        # use token
        user_token.available_request -= 1

        session.commit()

    @add_app_context(application.app_context())
    @create_scoped_session()
    def make_comment_and_send_mail_if_request_available(self, session, video_history, comment, user_history, lock):

        user = User.get_user(session, video_history.user_id)
        user_token = session.query(Token).filter_by(user_id=user.id).first()

        # use lock to ensure user_token data intergrity
        lock.acquire()

        if user_token.available_request > 0:

            video_id = video_history.video['id']
            comment_id = self.make_comment(video_id, comment)

            video_history.comment_id = comment_id
            print(f"commented for {user.id} here https://www.youtube.com/watch?v={video_id}&lc={comment_id}")
            user_token.available_request -= 1

            # inserting video history
            session.add(video_history)

            # send mail
            user.send_mail(video_history)
            print(f"comment mail sent to user {user.name}")


        else:
            user_history.append(video_history)

        lock.release()




class DeveloperYoutube(Youtube):

    def __init__(self, developer_key):
        from googleapiclient.discovery import build

        youtube = build('youtube', 'v3', developerKey=developer_key)
        super().__init__(youtube)

    def get_channel_from_id(self, channel_id):
        channel_request = self.__youtube.channels().list(
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
        video_request = self.__youtube.videos().list(
            part="snippet",
            id=video_id
        )
        video_response = video_request.execute()
        return video_response

    def api_activity(self, channel_id):

        activity_request = self.__youtube.activities().list(
            part= "snippet,contentDetails",
            channelId= channel_id,
            maxResults = 20
        )
        activity_response = activity_request.execute()
        return activity_response


    # def extract_video(self, channel_id, tag_list, last_fetch_time):




from env_details import env_details
youtube = DeveloperYoutube(developer_key=env_details['YT_API_KEY'])

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
    def get_latest_videos(youtube, channel_id, last_fetch_time):
        from datetime import datetime
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

            video = Video(id=id, title=title, link=video_link, time=str_publish_time, description=description)

            result.append(video)

        return result, current_time