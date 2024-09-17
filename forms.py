from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Контент', validators=[DataRequired()])
    images = MultipleFileField('Картинки', description='Upload images (optional)')
    submit = SubmitField('Опубликовать')
