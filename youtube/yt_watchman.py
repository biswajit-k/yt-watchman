import threading
import logging
from itertools import groupby
from collections import defaultdict
from operator import attrgetter
from sqlalchemy.exc import SQLAlchemyError

from settings import application
from thread_safe_utils import create_scoped_session, add_app_context
from models.subscription import Subscription
from models.token import Token
from models.history import History
from models.user import User
from youtube.youtube import Video
from youtube.mail_sender import send_mail


@add_app_context(application.app_context())
@create_scoped_session    # don't want to expire objects as co
def yt_watchman(session):
  """
    algorithm:
      - group subscriptions by channel and fetch latest videos by channel(last fetch time of channel -
        i currently find this by last fetch time of any subscription of that channel)
      - check if videos match subscription - then append history for that subscription
        also, comment in a separate thread
      - do for all users
      - you get list of {recipients:history_found}
      - send mail to each recipient group videos by subscription(1. mailing list for livlyf 2. mailing list for bandhu...)

      shortcomings
      - new sub. created after watchman ran: if new video is published before watchman is finished - it won't be detected(rare)
      - same if sub. moved from paused to active(rare)
      - after deleting sub. while watchman is running and matching video comes and if it has comment enabled - it will comment on it
      and mail you but not shown in dashboard
  """
  print("yt_watchman core activated!\n")

  from application import youtube

  # core logic
  all_subscriptions = session.query(Subscription).filter_by(active=True).order_by(
                  Subscription.channel_id, Subscription.last_fetched_at).all()
  channel = [list(g) for k, g in groupby(all_subscriptions, attrgetter('channel_id'))]

  all_history: list[History] = []
  user_youtube = {}
  user_lock = {}

  for subscriptions in channel:

    # get channel details, check if new video on channel uploaded -> then check for all subs. if it matches
    channel_id = subscriptions[0].channel_id
    last_fetched_at = subscriptions[0].last_fetched_at

    #### get latest videos for oldest fetch time sub - for each sub iterate list from pos after its last fetch time
    latest_videos, fetch_time = Video.get_latest_videos(youtube, channel_id, last_fetched_at)

    for sub in subscriptions:
      user = User.get_user(session, sub.user_id)

      if user is None:
        continue

      user_token = Token.get_token(session, user.id)

      sub.last_fetched_at = fetch_time

      for video in latest_videos:

        matching_tag = video.get_matching_tag(sub.tags)
        if not matching_tag:
          continue

        video_history = History(user_id=user.id, video_id=video.id, video_title=video.title, channel_id=channel_id, tag=matching_tag, found_at=fetch_time)

        if user.id not in user_youtube:
          user_youtube[user.id] = user.get_youtube()
          user_lock[user.id] = threading.Lock()

        user_yt = user_youtube[user.id]
        # create a lock on token(while not lock:) inside make comment and release after - return comment details then send mail
        # for comment separately

        in_comment_thread = False
        if (sub.comment and user_yt and user_token.available_request > 0):
          user_lock[user.id].acquire()
          print("acquired lock for comment")
          session.refresh(user_token)
          if(user_token.available_request > 0):
            print("starting comment thread")
            in_comment_thread = True
            comment_thread = threading.Thread(daemon=True, target=user_yt.make_comment,
                      args=(video_history, user.id, sub.comment, user_lock[user.id]))
            comment_thread.start()
          else:
            user_lock[user.id].release()
            print("released lock")

        if not in_comment_thread:
          try:
            all_history.append(video_history)   # add matching video w/o comment in history
            session.add(video_history)
            session.commit()
          except SQLAlchemyError as e:
            session.rollback()
            all_history.pop()
            logging.error("Error while completing transaction for subscription-\n%s", e)


  mail_recipients = defaultdict(lambda: defaultdict(list))
  for history in all_history:
    user = User.get_user(session, history.user_id)
    subscription = history.get_subscription()
    for recipient_email in subscription.emails: # type:ignore
      mail_recipients[recipient_email][user.name].append(history)

  for recipient_email, recipient_users in mail_recipients.items():
    subject = "Youtube Watchman | Video detected!"
    subscriptions = []

    body = "Hey,\nWe have found videos that match your recommendation.\n\n"
    for username, history_list in recipient_users.items():
      body += f"Videos from the mailing list of {username}-\n"
      video_content = []
      for history in history_list:
        video_content.append(f"""Title- {history.video_title}\nLink- {"https://www.youtube.com/watch?v=" + history.video_id}
Time(in UTC)- {history.found_at}\nTag Detected- {history.tag}""")
      body += "\n\n".join(video_content)

    threading.Thread(daemon=True, target=send_mail,
                    args=(recipient_email, subject, body)).start()
    print(f"{recipient_email} done!")

  session.commit()
