from datetime import datetime
from settings import db, ma


class History(db.Model):
    video_id = db.Column(db.String(80), primary_key=True, nullable=True)
    user_id = db.Column(db.String(80), primary_key=True, nullable=False)
    channel_id = db.Column(db.String(120), nullable=False)
    tag = db.Column(db.String(120), nullable=False)
    found_at = db.Column(db.DateTime, default=datetime.now)
    comment_id = db.Column(db.String(120), nullable=False, default='')

    def __repr__(self) -> str:
        return f'''video_id- {self.video_id} \n
        channel_id- {self.channel_id} \n
        tag- {self.tag}  \n
        user_id- {self.user_id}  \n
        comment_id- {self.comment_id}  \n
        found_at- {self.found_at} \n'''


class HistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = History


history_schema = HistorySchema(many=True)


def delete_history(user_id):
    db.session.query(History).filter_by(user_id=user_id).delete()
    db.session.commit()
