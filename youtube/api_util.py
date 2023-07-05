import datetime
from youtube.get_video_id import get_yt_video_id

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

# token present and not expired. delete token if expired
def get_credentials(user_id):
    from settings import db
    from models.token import Token
    from youtube.env_details import env_details
    client_id = env_details['CLIENT_ID']
    client_secret = env_details['CLIENT_SECRET']
    refresh_token = db.session.query(Token).filter_by(user_id=user_id).first()
    if refresh_token is None:
        print(f"WARN: user_id-{user_id} token not found")
        return None
    refresh_token = refresh_token.refresh_token
    access_token = get_access_token(client_id, client_secret, refresh_token)
    if access_token is None:
        print(f"WARN: user_id-{user_id} token expired")
        db.session.query(Token).filter_by(user_id=user_id).delete()
        db.session.commit()
        return None
    credentials = {
    'token': access_token,
    'refresh_token': refresh_token,
    'token_uri': 'https://www.googleapis.com/oauth2/v3/token',
    'client_id': client_id,
    'client_secret': client_secret,
    }
    return credentials


def get_youtube(user_id):
    from google.oauth2 import credentials
    import googleapiclient

    user_credentials = get_credentials(user_id)
    if user_credentials is None:
        return None
    cred = credentials.Credentials(**user_credentials)
    youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=cred)
    return youtube

def get_user_channel(user_id):

    youtube = get_youtube(user_id)
    if youtube is None:
        return None

    channel_request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        mine=True
    )
    channel_response = channel_request.execute()
    return channel_response

def get_channel_from_id(youtube, channel_id):
    channel_request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    channel_response = channel_request.execute()

    def human_format(num, round_to=2):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num = round(num / 1000.0, round_to)
        return '{:.{}f}{}'.format(num, round_to, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

    subscribers = human_format(int(channel_response["items"][0]["statistics"]["subscriberCount"]))
    return {
        "title": channel_response["items"][0]["snippet"]["title"],
        "imgUrl": channel_response["items"][0]["snippet"]["thumbnails"]["default"]["url"],
        "subscribers": subscribers,
        "videos": int(channel_response["items"][0]["statistics"]["videoCount"]),
        "id": channel_id,
    }

def get_channel_id_from_url(url):
    import requests
    import re
    r = requests.get(url)
    # print(r.status_code)
    # print("get channelId error- " + r.raise_for_status())
    page_source = r.text
    channel_id = re.search(r"<link\ rel=\"canonical\"\ href=\"https://www\.youtube\.com/channel/(.*?)\"", page_source).group(1)
    return channel_id

def get_video(youtube, video_id):
    video_request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    video_response = video_request.execute()
    return video_response

def get_channel_id_from_video(youtube, video_link):

    video_id = get_yt_video_id(video_link)
    if(video_id == None):
        return "-1"

    video_response = get_video(youtube, video_id)
    return video_response["items"][0]["snippet"]["channelId"]


def api_video_count(youtube, channelId):

    channel_request = youtube.channels().list(
            part="statistics",
            id=channelId
    )

    channel_response = channel_request.execute()
    video_count = channel_response["items"][0]["statistics"]["videoCount"]
    return video_count

def api_activity(youtube, channelId):

    activity_request = youtube.activities().list(
        part= "snippet,contentDetails",
        channelId= channelId,
        maxResults = 40
    )
    activity_response = activity_request.execute()
    return activity_response

def extract_video(youtube, channelId, tag_list, last_fetch_time):

    response = api_activity(youtube, channelId)
    result = []
    current_time = datetime.datetime.now()
    for video in response["items"]:
        if(video["snippet"]["type"] != "upload"):           # playlistItem maybe
            continue
        publish_time = datetime.datetime.strptime(video["snippet"]["publishedAt"][:19], '%Y-%m-%dT%H:%M:%S')
        if(publish_time <= last_fetch_time):
            break
        str_publish_time = publish_time.strftime("%m/%d/%Y, %H:%M:%S")
        title = video["snippet"]["title"]
        description = video["snippet"]["description"]
        video_id = video['contentDetails']['upload']['videoId']
        video_link = "https://www.youtube.com/watch?v=" + video_id


        search_text = description.split() + title.split()
        for word in search_text:
            yes = 0
            for tag in tag_list:
                if(tag.lower() == word.lower()):
                    vid = {
                        "title": title,
                        "link": video_link,
                        # "description": description,
                        "time": str_publish_time ,
                        "tag": tag,
                        "id": video_id,
                    }
                    result.append(vid)
                    yes = 1
                    break

            if(yes == 1):
                break

    last_fetch_time = current_time

    return result, last_fetch_time

def get_access_token(client_id, client_secret, refresh_token):
    import requests

    params = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token
    }

    authorization_url = "https://oauth2.googleapis.com/token"

    r = requests.post(authorization_url, data=params)

    if r.ok:
            return r.json()['access_token']
    else:
            return None
