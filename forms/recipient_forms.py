from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class RecipientForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired(), Length(max=255)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    is_active = BooleanField("Активен")
    submit = SubmitField("Сохранить")


class TestEmailForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    submit = SubmitField("Отправить тест")

