from db import db


class AuthorModel(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    mfa = db.Column(db.String(4))
    token = db.Column(db.String(32))
