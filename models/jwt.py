from db import db
from datetime import date


class BlocklistJwt(db.Model):
    __tablename__ = "blocklistjwt"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.Date, default=date.today, nullable=False)
