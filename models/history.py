from sqlalchemy.orm.session import object_session
from sqlalchemy import ForeignKeyConstraint

from models.subscription import Subscription
from settings import db, ma
from utils.utilities import parse_date, get_utc_now, get_duration_seconds


class History(db.Model):
    video_id = db.Column(db.String(80), primary_key=True, nullable=False)
    user_id = db.Column(db.String(80), primary_key=True, nullable=False)
    channel_id = db.Column(db.String(120), nullable=False)
    video_title = db.Column(db.String(120), nullable=False)
    tag = db.Column(db.String(120), nullable=False)
    found_at = db.Column(db.DateTime, default=get_utc_now())
    comment_id = db.Column(db.String(120), nullable=False, default='')

    __table_args__ = (ForeignKeyConstraint([user_id, channel_id],
                                           [Subscription.user_id, Subscription.channel_id]), {})

    def __repr__(self) -> str:
        return f'''video_id- {self.video_id} \n
        video_title- {self.video_title} \n
        channel_id- {self.channel_id} \n
        tag- {self.tag}  \n
        user_id- {self.user_id}  \n
        comment_id- {self.comment_id}  \n
        found_at- {self.found_at} \n'''

    def get_subscription(self):
        return object_session(self).query(Subscription).filter_by(user_id=self.user_id, channel_id=self.channel_id).first() # type:ignore

    # @classmethod
    # def upsert(cls, session, data, key_columns=[]):
    #     """ function to insert(or update if already present) the data into model.
    #     conflict will be decided by concatination of `key_columns` + `id` columns
    #     if same concat other record present then update else insert.
    #     It is thread-safe """

    #     stmt = insert(cls).values(data.__dict__)

    #     # Important to exclude the ID for update!
    #     exclude_for_update = [cls.video_id.name, cls.channel_id.name, *key_columns]
    #     update_dict = {c.name: c for c in stmt.excluded if c.name not in exclude_for_update}
    #     print(update_dict)

    #     stmt = stmt.on_conflict_do_update(
    #         index_elements=key_columns,
    #         set_=update_dict
    #     ).returning(cls)

    #     orm_stmt = (
    #         select(cls)
    #         .from_statement(stmt)
    #         .execution_options(populate_existing=True)
    #     )

    #     print("the raw upsert query:")
    #     from sqlalchemy.dialects import postgresql
    #     print(orm_stmt.compile(dialect=postgresql.dialect()))
    #     return session.execute(orm_stmt).scalar()


    @classmethod
    def normalize(cls, history_dic):
        import copy
        import humanize
        from application import youtube

        history = copy.copy(history_dic)

        abc = youtube.get_video(history['video_id'])
        print("abc is:")
        print(abc)
        if len(abc['items']) == 0:
            print(f"video id: {history['video_id']}")
        video = abc['items'][0]

        history['imgUrl'] = video['snippet']['thumbnails']['high']['url']
        history['video_title'] = video['snippet']['title']
        history['channel_title'] = video['snippet']['channelTitle']

        time_found = get_duration_seconds(parse_date(history["found_at"]))
        if (divmod(time_found, 3600)[0] < 24):
            history["found_at"] = f"Found {humanize.naturaldelta(time_found)} ago"
        else:
            date = parse_date(history["found_at"])
            history["found_at"] = f"Found on {date.day} {date.strftime('%B')}, {date.year}"
        return history


class HistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = History


history_schema = HistorySchema(many=True)
