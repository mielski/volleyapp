from typing import cast
from http import HTTPStatus

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
    """

    :return: json with following keys:
    - acknowlegded: true or false based whether created was successful
    - id: the id of the new exercise
    """

    data = request.get_json()
    try:
        exercise = ExerciseModel.parse_obj(data)
    except ValidationError as error:
        raise InvalidPayload("bad request: invalid exercise payload", error) from None
    result = app.db.exercises.insert_one(exercise.model_dump(by_alias=True))
    return jsonify({"acknowledged": result.acknowledged, "id_": result.inserted_id}), HTTPStatus.CREATED

@exercises_api_bp.get("/")
def get_exercises():
    """Get all exercises as a list"""

    data = [exercise for exercise in app.db.exercises.find()]
    return jsonify(data), HTTPStatus.OK


@exercises_api_bp.put("/<string:_id>/")
def update_exercise(_id):
    """update the information of the exercise"""

    exercise_data = dict(app.db.exercises.find_one({"_id": _id}))
    if exercise_data is None:
        abort(HTTPStatus.NOT_FOUND, "no exercise found for id")

    data = request.get_json()
    exercise_data.update(data)
    try:
        exercise = ExerciseModel.parse_obj(exercise_data)
    except ValidationError as error:
        raise InvalidPayload("bad request: invalid exercise payload", error) from None

    app.db.exercises.update_one({"_id": _id}, exercise.model_dump(by_alias=True, exclude={"id"}))

