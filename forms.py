from flask_wtf import FlaskForm
from wtforms import (
    FileField,
    StringField,
    TextAreaField,
    SubmitField
)
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField(
        'Заголовок',
        validators=[DataRequired()]
    )
    content = TextAreaField(
        'Контент',
        validators=[DataRequired()]
    )
    images = FileField(
        'Картинки',
        validators=[DataRequired()],
        description='Upload images (optional)'
    )
    submit = SubmitField(
        'Опубликовать'
    )
