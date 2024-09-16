from datetime import date

from constants import (
    LENGHT_JTI,
    LENGHT_CONTENT,
    LENGHT_TITLE,
    LENGHT_USERNAME,
    LENGHT_PASSWORD,
    LENGHT_TOKEN
)
from db import db


class BlocklistJwt(db.Model):
    __tablename__ = "blocklistjwt"
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    jti = db.Column(
        db.String(LENGHT_JTI),
        nullable=False,
        index=True
    )
    created_at = db.Column(
        db.Date,
        default=date.today,
        nullable=False
    )

class ProjectModel(db.Model):
    __tablename__ = 'projects'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    date = db.Column(
        db.Date,
        default=date.today
    )
    content = db.Column(
        db.String(LENGHT_CONTENT),
        nullable=False
    )
    title = db.Column(
        db.String(LENGHT_TITLE),
        nullable=False
    )
    likes_count = db.Column(
        db.Integer,
        default=0
    )
    likes = db.relationship(
        'LikeModel',
        back_populates='project'
    )

class LikeModel(db.Model):
    __tablename__ = 'likes'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id')
    )
    author_id = db.Column(
        db.Integer,
        db.ForeignKey('author.id')
    )
    project = db.relationship(
        'ProjectModel',
        back_populates='likes'
    )
    author = db.relationship(
        'AuthorModel',
        back_populates='likes'
    )

class AuthorModel(db.Model):
    __tablename__ = 'author'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(LENGHT_USERNAME),
        nullable=False
    )
    password = db.Column(
        db.String(LENGHT_PASSWORD),
        nullable=False
    )
    token = db.Column(
        db.String(LENGHT_TOKEN)
    )
    likes = db.relationship(
        'LikeModel',
        back_populates='author'
    )
    first_name = db.Column(
        db.String(LENGHT_USERNAME)
    )
    last_name = db.Column(
        db.String(LENGHT_USERNAME)
    )
    cityzen_id = db.Column(
        db.String(LENGHT_TOKEN)
    )
    privileges = db.Column(
        db.Integer, default=0
    )
