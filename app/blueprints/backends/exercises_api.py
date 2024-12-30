from typing import cast

from flask import abort, Blueprint, current_app, jsonify
from pydantic import ValidationError

from app.forms import VolleyballExerciseForm
from app.models import ExerciseModel
from app.training_app import MyTrainingsApp

exercises_api_bp = Blueprint('exercises_api', __name__, url_prefix="api/exercises", template_folder="templates")

app = cast(MyTrainingsApp, current_app)

@exercises_api_bp.route("/", method=["POST"])
def create_exercise(exercise_data: str):

    try:
        exercise = ExerciseModel.parse_raw(exercise_data)
    except ValidationError as error:
        return jsonify(error), 500
    result = app.db.exercises.insert_one(exercise.model_dump(by_alias=True))
    return jsonify(result), 201
