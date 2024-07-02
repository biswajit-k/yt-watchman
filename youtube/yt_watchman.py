import datetime
import threading
from itertools import groupby
from collections import defaultdict
from operator import attrgetter
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from application import application
from thread_safe_utils import add_app_context
from models.subscription import Subscription
from models.history import History
from models.user import Token
from models.user import User
from models.db_utils import non_expiring_session
from utils.utilities import MyException
from youtube.youtube import Video
from youtube.mail_sender import EmailService

# objects will get expired on commit
@add_app_context(application.app_context())
def yt_watchman():
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


      async function to handle each "subscription"/"user" - put all of them in a list run async fun() on each - save lot of time
      as the thread will keep jumping b/w each "subscription"/"user" when their data is being fetched/stored/etc
  """
  print("yt_watchman core activated!\n")

  from application import youtube

  # core logic
  all_subscriptions = non_expiring_session  \
                      .query(Subscription)  \
                      .filter_by(active=True) \
                      .order_by(Subscription.channel_id)  \
                      .all()
  channel = [list(g) for k, g in groupby(all_subscriptions, attrgetter('channel_id'))]

  all_history: list[History] = []
  user_youtube = {}

  for subscriptions in channel:

    # get channel details, check if new video on channel uploaded -> then check for all subs. if it matches
    channel_id = subscriptions[0].channel_id
    last_video_id_fetched = subscriptions[0].last_video_id_fetched
    #### get latest videos for oldest fetch time sub - for each sub iterate list from pos after its last fetch time
    try:
      fetch_time = datetime.datetime.now(datetime.UTC)
      latest_videos, latest_video_id = Video.get_latest_videos(youtube, channel_id, last_video_id_fetched)
      print(f"latest videos: {len(latest_videos)}")
    except MyException as e:
      return

    for sub in subscriptions:
      user = non_expiring_session.query(User).filter_by(id=sub.user_id).first()

      if user is None:
        continue

      user_token = non_expiring_session.query(Token).filter_by(user_id=user.id).first()

      if user_token is None:
        continue

      non_expiring_session.refresh(user_token)

      sub.last_video_id_fetched = latest_video_id

      for video in latest_videos:

        matching_tag = video.get_matching_tag(sub.tags)
        if not matching_tag:
          continue

        print("video matched")
        video_history = History(user_id=user.id, video_id=video.id, video_title=video.title,
                                channel_id=channel_id, tag=matching_tag, found_at=fetch_time)
        video_history.video_link = video.link
        video_history.thumbnail_url = video.thumbnail_url
        video_history.channel_title = video.channel_title
        video_history.video_description = video.description

        if user.id not in user_youtube:
          user_youtube[user.id] = user.get_youtube()

        user_yt = user_youtube[user.id]

        if (sub.comment and user_yt and user_token.available_request > 0):
            comment_thread = threading.Thread(daemon=True, target=user_yt.handle_comment,
                      args=(video_history, user.id, sub.comment))
            comment_thread.start()

        # commit each history separately so that if one fails for some reason
        # then previous history persists
        try:
          all_history.append(video_history)   # add matching video w/o comment in history
          non_expiring_session.add(video_history)
          non_expiring_session.commit()
        except SQLAlchemyError as e:
          non_expiring_session.rollback()
          all_history.pop()
          if isinstance(e, IntegrityError):
              print("Not inserting! Same history with comment info. already exist!")
          else:
              print("Error while completing transaction for subscription-\n%s", e)


  mail_recipients = defaultdict(lambda: defaultdict(list))
  for history in all_history:
    user = User.query.filter_by(id=history.user_id).one()
    subscription = history.get_subscription()
    for recipient_email in subscription.emails: # type:ignore
      mail_recipients[recipient_email][user.name].append(history)

  EmailService.send_history_mail(mail_recipients)

  non_expiring_session.commit()
