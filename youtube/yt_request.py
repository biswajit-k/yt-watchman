from googleapiclient.discovery import build
from youtube.env_details import env_details
from  youtube.mail_sender import send_mail
from youtube.api_util import extract_video


api_key = env_details['YT_API_KEY']
SENDER_EMAIL = env_details['SENDER_EMAIL']
SENDER_PASS = env_details['SENDER_PASS']

youtube = build('youtube', 'v3', developerKey=api_key)


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

def send_emails(user, findings, recipients):
    for recipient_email, sub_ids in recipients.items():
        
        subject = "Youtube Watchman | Video detected!"
        mail_str = ""
        mail_result_list = []

        for sub_id in sub_ids:
            channel_title = findings[sub_id][0]
            videos = findings[sub_id][1]
            for video in videos:
                mail_video = f"""Title- {video["title"]}\nLink- {video["link"]}\nTime- {video["time"]}\nTag Detected- {video["tag"]}"""
                mail_result_list.append(mail_video)
            nl = '\n'
            mail_str += f"""Channel- {channel_title}{nl}{(nl + nl).join(mail_result_list)}{nl + nl}"""

        mail_content = (f"""Hey Subscriber!{nl}You are a part of mailing list of {user.name}({user.email}). We detected below videos according to your preference -
    {nl}{mail_str}
    """)
        send_mail(SENDER_EMAIL, SENDER_PASS, recipient_email, subject, mail_content)



def make_comment(youtube, video_id, comment):
    request = youtube.commentThreads().insert(
        part="snippet",
        body={
          "snippet": {
            "videoId": video_id,
            "topLevelComment": {
              "snippet": {
                "textOriginal": comment
              }
            }
          }
        }
    )
    response = request.execute()    
    return response['id']



if(__name__ == "__main__"):
    # print(env_details)
    quiz_tag = ['quiz', 'voucher', 'gift']
    timer(send_subscriber_mail, youtube, env_details["SAMPLE_CHANNEL_ID"], quiz_tag, env_details["SENDER_EMAIL"], env_details["SENDER_PASS"], env_details["RECEIVER_LIST"], 10)
