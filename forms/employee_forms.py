from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import DateField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class EmployeeForm(FlaskForm):
    company_name = StringField(
        "Наименование предприятия",
        validators=[DataRequired(), Length(max=255)],
    )
    full_name = StringField("ФИО", validators=[DataRequired(), Length(max=255)])
    position = StringField("Должность", validators=[DataRequired(), Length(max=255)])
    department = StringField("Подразделение", validators=[Optional(), Length(max=255)])
    birth_date = DateField("Дата рождения", format="%Y-%m-%d", validators=[DataRequired()])
    notes = TextAreaField("Комментарий", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Сохранить")


class ImportForm(FlaskForm):
    file = FileField(
        "Excel-файл",
        validators=[FileRequired(), FileAllowed(["xlsx"], "Разрешены только .xlsx файлы.")],
    )
    submit = SubmitField("Импортировать")

