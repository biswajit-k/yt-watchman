import atexit
from itertools import groupby
from operator import attrgetter
from youtube.api_util import get_youtube
from settings import Db_scoped_session
from utils.utilities import get_field_default, time_diff, get_utc_now
from models.subscription import Subscription
from models.token import Token
from models.history import History
from models.user import User
from youtube.api_util import extract_video, get_channel_from_id
from youtube.yt_request import youtube, send_emails, make_comment


# session exit handler
def exit_handler(session):
  if session.is_active:
      print("abort... abrupt closing session!")
      session.close()


# TODO: send_mails can be set as webhook - is it required?
def yt_watchman(app_context):

  # push app context as part of thread so don't get app context automatically
  app_context.push()
  print("yt_watchman core activated!\n")

  try:

    session = Db_scoped_session()

    # handle abrupt program termination
    atexit.register(exit_handler, session=session)


    # core logic
    all_subscriptions = session.query(Subscription).filter_by(active=True).order_by(Subscription.user_id).all()
    user_subscriptions = [list(g) for k, g in groupby(all_subscriptions, attrgetter('user_id'))]
    for subscriptions in user_subscriptions:

      user = session.query(User).filter_by(id=subscriptions[0].user_id).first()
      user_token = session.query(Token).filter_by(user_id=subscriptions[0].user_id).first()
      findings = {}
      recipients = {}

      for sub in subscriptions:

        video_list, fetch_time = extract_video(youtube, sub.channel_id, sub.tags, sub.last_fetched_at)

        sub.last_fetched_at = fetch_time

        # break
        if(len(video_list) != 0):
          channel_title = get_channel_from_id(youtube, sub.channel_id)['title']
          findings[sub.id] = [channel_title, video_list]
          normalized_videos = []
          for email_id in sub.emails:
            if email_id not in recipients:
              recipients[email_id] = []
            recipients[email_id].append(sub.id)

          tokenized_youtube = get_youtube(sub.user_id)

          if(tokenized_youtube != None):
            diff = time_diff(get_utc_now(), user_token.reset_time)
            if(diff >= 86400):
              user_token.available_request = get_field_default(Token, "available_request")
              user_token.reset_time = get_utc_now()

          for video in video_list:
            history = normalize_video(video, sub, fetch_time)

            if((tokenized_youtube != None) and (sub.comment != '') and (user_token.available_request > 0)):
              comment_id = make_comment(tokenized_youtube, video['id'], sub.comment)
              history.comment_id = comment_id
              print(f"commented for {sub.user_id} here https://www.youtube.com/watch?v={video['id']}&lc={comment_id}")
              user_token.available_request -= 1
              print(f"req. available - {user_token.available_request}")
            normalized_videos.append(history)

          session.add_all(normalized_videos)
        session.commit()
      send_emails(user, findings, recipients)
      print(f"{user.name} done!")

    print("-----all mails sent! ------")

  finally:
    print("session closing\n")
    session.close()

def normalize_video(video, sub, fetch_time):
  vid = History(video_id=video['id'], channel_id=sub.channel_id, tag=video['tag'], found_at=fetch_time, user_id=sub.user_id, comment_id='')
  return vid
