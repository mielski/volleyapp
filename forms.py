import datetime

import flask_wtf
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TextAreaField, SelectField, \
    IntegerField
from wtforms.validators import DataRequired, Length

class HelloForm(flask_wtf.FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 150)])
    remember = BooleanField('Remember me')
    submit = SubmitField()


class TrainingForm(flask_wtf.FlaskForm):
    """form to fill in the main attributes of a training"""
    title = StringField('Title', validators=[DataRequired()],
                        description="The title of the training.")
    date = DateField("Date", validators=[DataRequired()])
    submit = SubmitField()


class TrainingFormDetailed(TrainingForm):

    description = TextAreaField("Description")
    rating = SelectField("Rating", choices=[0, 1, 2, 3, 4, 5])
    attendees = IntegerField("Number of Players")
    # tags = TagsField()  TODO create a custom field for this
    submit = SubmitField()
    notes = TextAreaField("Notes")
