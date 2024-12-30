from typing import cast

from flask import abort, Blueprint, current_app, jsonify, make_response, request
from pydantic import ValidationError

from app.errors import InvalidPayload
from app.models import ExerciseModel
from app.training_app import MyTrainingsApp

exercises_api_bp = Blueprint('exercises_api', __name__, url_prefix="/api/exercises")

app = cast(MyTrainingsApp, current_app)


@exercises_api_bp.errorhandler(InvalidPayload)
def handle_invalid_payload(error: InvalidPayload):

    response = jsonify(error.error_list)
    response.status_code = error.status_code
    return response

@exercises_api_bp.post("/")
def create_exercise():

    data = request.get_json()
    try:
        exercise = ExerciseModel.parse_obj(data)
    except ValidationError as error:
        raise InvalidPayload("bad request: invalid exercise payload", error) from None
    app.db.exercises.insert_one(exercise.model_dump(by_alias=True))
    return exercise.model_dump(by_alias=True, mode="json"), 201
