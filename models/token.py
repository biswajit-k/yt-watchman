from datetime import datetime
from settings import db, ma


class Token(db.Model):
    user_id = db.Column(db.String(120), db.ForeignKey('user.id'),
                        primary_key=True)
    refresh_token = db.Column(db.String(120), nullable=False)
    available_request = db.Column(db.Integer, default=1)
    reset_time = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f'''user_id- {self.user_id} \n
      refresh_token- {self.refresh_token} \n
      reset_time- {self.reset_time} \n
      available_request- {self.available_request} \n'''


class TokenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Token


token_schema = TokenSchema()


def delete_token(user_id):
    token = db.session.query(Token).filter_by(user_id=user_id).delete()
    db.session.commit()
