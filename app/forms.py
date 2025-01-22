import datetime
from enum import Enum

import flask_wtf
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TextAreaField, SelectField, \
    IntegerField, FieldList, SelectMultipleField, URLField, DateTimeLocalField, MultipleFileField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, URL

from .models import TrainingModel, ExerciseModel, Skills, DifficultyLevel


class ListStringField(TextAreaField):
    """specialized TextAreaField that stored string as elements split by
    newlines."""

    def process_formdata(self, valuelist):
        """splits formstring per line and stores elements as data"""

        if valuelist and valuelist[0]:

            self.data = [item.strip() for item in valuelist[0].split("\n")]
        else:
            self.data = []

    def _value(self):
        """set formstring from data elements"""

        return "\n".join(self.data) if self.data else ""


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

    @classmethod
    def from_model(cls, training: TrainingModel):
        return cls(title=training.title, date=training.training_date)


class TrainingFormDetailed(TrainingForm):
    description = TextAreaField("Description")
    rating = SelectField("Rating", choices=[0, 1, 2, 3, 4, 5])
    attendees = IntegerField("Number of Players")
    # tags = TagsField()  TODO create a custom field for this
    notes = TextAreaField("Notes")
    submit = SubmitField()

    @classmethod
    def from_model(cls, training: TrainingModel):
        return cls(
            title=training.title,
            date=training.training_date,
            description=training.description,
            rating=training.rating,
            attendees=training.attendees,
            notes=training.notes
        )

class EnumSelectorField(SelectMultipleField):
    """specialized class to work with Enumeration fields,

    Two overrides:
    in constructor: choices should be an Enum and this is coersed into its underlying member values
    to acts as a normal list of string choises

    on loading data into the form: enumeration data is turned into strings.
    """

    def __init__(self, label=None, validators=None, coerce=str, choices=None, validate_choice=True, **kwargs):
        if choices:
            choices = [(member.value, member.value) for member in choices]
        super().__init__(label, validators, coerce, choices, validate_choice, **kwargs)

    @staticmethod
    def _process_data_item(enum_value):
        """turns any enumeration type into a string representation of its value attribute"""

        try:
            return enum_value.value
        except (TypeError, AttributeError):
            return enum_value

    def process_data(self, value):
        if value is not None:
            value = [self._process_data_item(v) for v in value]
        super().process_data(value)


class VolleyballExerciseForm(flask_wtf.FlaskForm):
    """form used to view and edit volleybal exercises"""
    title = StringField("Title", validators=[DataRequired()])
    approach = TextAreaField("Approach", default="", description="Describe the exercise approach")
    player_roles = ListStringField("Player Roles", description="Roles used in the approach",
                                   default=""
                                   )
    difficulty_level = SelectField("Difficulty Level",
                                   choices=[(member.value, member.value) for member in DifficultyLevel],
                                   default="Easy",
                                   validators=[DataRequired()])

    duration = StringField("Duration of the exercise", default="10",
                           description="Non-negative duration in minutes")

    skill_focus = EnumSelectorField("Skill Focus", choices=Skills,)

    intensity = IntegerField("Intensity", validators=[Optional(), NumberRange(min=1, max=5)],
                             description="1=low, 5=high")

    video_url = URLField("Video URL", validators=[Optional(), URL()])

    new_images = MultipleFileField("Upload new images", id="new_images", render_kw={"accept": "image/png, image/jpeg"})
    image_uris = FieldList(URLField("Image URI", validators=[URL()]), description="URLs for exercise images")

    tags = FieldList(StringField("Tag"), description="Tags for the exercise")

    # related_exercises = FieldList(StringField("Related Exercise ID"), description="IDs of related exercises")
    @classmethod
    def from_exercise(cls, exercise: ExerciseModel):
        return cls(
            title=exercise.title,
            approach=exercise.approach,
            difficulty_level=exercise.difficulty_level.value,
            duration=exercise.duration,
            skill_focus=exercise.skill_focus,
            intensity=exercise.intensity,
            video_url=exercise.video_url,
            image_uris=exercise.image_blob_urls,
            tags=exercise.tags
        )
