from db import db
from datetime import date


class ProjectModel(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    content = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(20), nullable=False)