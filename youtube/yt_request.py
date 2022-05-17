from googleapiclient.discovery import build
import datetime
from youtube.env_details import env_details

from  youtube.mail_sender import send_mail
from youtube.api_util import extract_video

api_key = env_details['YT_API_KEY']
youtube = build('youtube', 'v3', developerKey=api_key)

# 4 march 22
last_fetch_time = datetime.datetime.strptime("2022-03-04T00:00:00", '%Y-%m-%dT%H:%M:%S')


quiz_tag = ["quiz", "INR", "$", "vouchers"]
my_file = "./store.txt"



def send_subscriber_mail(youtube, channelId, tag_list, SENDER_EMAIL, SENDER_PASS, RECEIVER_LIST):

    global last_fetch_time

    # subject
    subject = "Youtube Watchman | Video detected!"
    # content 
    result, new_time = extract_video(youtube, channelId, tag_list, last_fetch_time)

    last_fetch_time = new_time
    
    mail_result_list = []
    for video in result:
        mail_video = f"""Title- {video["title"]}\nLink- {video["link"]}\nTime- {video["time"]}\nTag Detected- {video["tag"]}"""
        mail_result_list.append(mail_video)

    mail_str = "\n\n".join(mail_result_list)
    content = (f"""Hey Subscriber!\n\nWe detected below videos according to your preference -
    \n{mail_str}
    """)
    # send mail
    send_mail(SENDER_EMAIL, SENDER_PASS, RECEIVER_LIST, subject, content)


def timer(action, youtube, channelId, tag_list, SENDER_EMAIL, SENDER_PASS, RECEIVER_LIST, delay):
    import time
    while True:
        action(youtube, channelId, tag_list, SENDER_EMAIL, SENDER_PASS, RECEIVER_LIST)
        time.sleep(delay)

# print(activity_response)

if(__name__ == "__main__"):
    # print(env_details)
    timer(send_subscriber_mail, youtube, env_details["SAMPLE_CHANNEL_ID"], quiz_tag, env_details["SENDER_EMAIL"], env_details["SENDER_PASS"], env_details["RECEIVER_LIST"], 10)
