from flask_wtf import FlaskForm
from wtforms import (
    MultipleFileField,
    StringField,
    TextAreaField,
    SubmitField
)
from wtforms.validators import DataRequired


class ApproveForm(FlaskForm):
    first_name = StringField(
        'Имя',
        validators=[DataRequired()]
    )
    last_name = StringField(
        'Фамилия',
        validators=[DataRequired()]
    )
    cityzen_id = StringField(
        'ID гражданина',
        validators=[DataRequired()],
    )
    submit = SubmitField(
        'Подтвердить'
    )


class PostForm(FlaskForm):
    title = StringField(
        'Заголовок',
        validators=[DataRequired()]
    )
    content = TextAreaField(
        'Контент',
        validators=[DataRequired()]
    )
    images = MultipleFileField(
        'Картинки',
        validators=[DataRequired()],
        description='Upload images (optional)'
    )
    submit = SubmitField(
        'Опубликовать'
    )
