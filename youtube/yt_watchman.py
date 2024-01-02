import threading
from itertools import groupby
from collections import defaultdict
from operator import attrgetter
from settings import application
from thread_safe_utils import create_scoped_session, add_app_context
from models.subscription import Subscription
from models.token import Token
from models.history import History
from models.user import User
from youtube.youtube import youtube, Video



@add_app_context(application.app_context())
@create_scoped_session()
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

  """
  print("yt_watchman core activated!\n")

  # core logic
  all_subscriptions = session.query(Subscription).filter_by(active=True).order_by(
                  Subscription.channel_id, Subscription.last_fetched_at).all()
  channel = [list(g) for k, g in groupby(all_subscriptions, attrgetter('channel_id'))]

  user_history = defaultdict(lambda: defaultdict(dict))
  user_youtube = {}
  user_lock = {}
  user_comment = {}

  for subscriptions in channel:

    # get channel details, check if new video on channel uploaded -> then check for all subs. if it matches
    channel_id = subscriptions[0].channel_id
    last_fetched_at = subscriptions[0].last_fetched_at

    #### get latest videos for oldest fetch time sub - for each sub iterate list from pos after its last fetch time
    latest_videos, fetch_time = Video.get_latest_videos(youtube, channel_id, last_fetched_at)

    for sub in subscriptions:

      user = User.get_user(session, sub.user_id)
      user_token = session.query(Token).filter_by(user_id=user.id).first()
      sub.last_fetched_at = fetch_time

      for video in latest_videos:

        matching_tag = video.get_matching_tag(sub.tags)
        if not matching_tag:
          continue

        video_history = History(user_id=user.id, video_id=video.id, video_title=video.title, channel_id=channel_id, tag=matching_tag, found_at=fetch_time)

        if user.id not in user_youtube:
          user_youtube[user.id] = user.get_youtube()
          user_lock[user.id] = threading.Lock()

        youtube = user_youtube[user.id]
        # create a lock on token(while not lock:) inside make comment and release after - return comment details then send mail
        # for comment separately

        if (sub.comment and youtube and user_token.available_request > 0):
          user_lock[user.id].acquire()
          if(user_token.available_request):
            comment_thread = threading.Thread(daemon=True, target=youtube.make_comment,
                      args=(video.id, sub.comment, user.id, user_comment))

            comment_thread.start()
            video_history.comment_id = user_comment[user.id]
            user_token.available_request -= 1

          user_lock[user.id].release()
          user.send_history_mail(video_history)
          user_history[user.id][sub.id]['history'].append(video_history)   # add matching video w/o comment in history

  all_history = []

  """
   history
    user_id:
      subscription_id:
        id, recipients, videos

  """


  for user_id, history_list in user_history:
    with user_lock[user_id]:
      all_history.extend(history_list)

  session.add_all(all_history)
  session.commit()

  # send mail
  all_users = session.query(User).all()
  for user in all_users:
    if user.id in user_history:
      user.send_mail(user_history[user.id])     # TODO: send mail from user - list of history
      print(f"{user.name} done!")

  print("-----all mails sent! ------")

    # TODO: commit only after certain logical group of things are done -- or use rollback to remove everything

        # break
        # if(len(video_list) != 0):
        #   channel_title = get_channel_from_id(youtube, sub.channel_id)['title']
        #   findings[sub.id] = [channel_title, video_list]
        #   normalized_videos = []
        #   for email_id in sub.emails:
        #     if email_id not in recipients:
        #       recipients[email_id] = []
        #     recipients[email_id].append(sub.id)

        #   tokenized_youtube = get_youtube(sub.user_id)

        #   if(tokenized_youtube != None):
        #     diff = time_diff(get_utc_now(), user_token.reset_time)
        #     if(diff >= 86400):
        #       user_token.available_request = get_field_default(Token, "available_request")
        #       user_token.reset_time = get_utc_now()

        #   for video in video_list:
        #     history = normalize_video(video, sub, fetch_time)

        #     if((tokenized_youtube != None) and (sub.comment != '') and (user_token.available_request > 0)):
        #       comment_id = make_comment(tokenized_youtube, video['id'], sub.comment)
        #       history.comment_id = comment_id
        #       print(f"commented for {sub.user_id} here https://www.youtube.com/watch?v={video['id']}&lc={comment_id}")
        #       user_token.available_request -= 1
        #       print(f"req. available - {user_token.available_request}")
        #     normalized_videos.append(history)

      #     session.add_all(normalized_videos)
      #   session.commit()
      # send_emails(user, findings, recipients)
