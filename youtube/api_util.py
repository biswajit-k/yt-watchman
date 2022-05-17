import datetime

from youtube.get_video_id import get_yt_video_id

def get_channel_from_video(youtube, video_link):
    
    video_id = get_yt_video_id(video_link)
    if(video_id == None):
        return "-1"
    channel_id_request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    channel_id_resopnse = channel_id_request.execute()

    return channel_id_resopnse["items"][0]["snippet"]["channelId"]


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
        maxResults = 200
    )
    activity_response = activity_request.execute()
    return activity_response

def extract_video(youtube, channelId, tag_list, last_fetch_time):

    response = api_activity(youtube, channelId)
    result = []
    current_time = datetime.datetime.now()

    for video in response["items"]:
        publish_time = datetime.datetime.strptime(video["snippet"]["publishedAt"][:19], '%Y-%m-%dT%H:%M:%S')
        if(publish_time <= last_fetch_time):
            break
        
        str_publish_time = publish_time.strftime("%m/%d/%Y, %H:%M:%S")
        title = video["snippet"]["title"]
        video_link = "https://www.youtube.com/watch?v=" + video["contentDetails"]["upload"]["videoId"] 
        description = video["snippet"]["description"] 

        for word in description.split():
            yes = 0
            for tag in tag_list:
                if(tag == word):
                    vid = {
                        "title": title, 
                        "link": video_link, 
                        # "description": description,
                        "time": str_publish_time , 
                        "tag": tag,
                    }
                    result.append(vid)
                    yes = 1
                    break

            if(yes == 1):
                break
    
    last_fetch_time = current_time

    # also return the updated time
    return result, last_fetch_time
