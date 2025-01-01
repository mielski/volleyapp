from typing import cast
from http import HTTPStatus

from flask import abort, Blueprint, current_app, jsonify, make_response, request
from pydantic import ValidationError

from app.errors import InvalidPayload
from app.models import ExerciseModel
from app.training_app import MyTrainingsApp

exercises_api_bp = Blueprint('exercises_api', __name__, url_prefix="/api/exercises")

app = cast(MyTrainingsApp, current_app)


@exercises_api_bp.errorhandler(404)
def not_found(error):
    response = jsonify(
        {"status": 404,
         "error": "Not Found",
         "message": f"The requested resource for id '{error.description}' was not found."}
    )
    return response, HTTPStatus.NOT_FOUND


@exercises_api_bp.errorhandler(InvalidPayload)
def handle_invalid_payload(error: InvalidPayload):
    response = jsonify(error.error_list)
    response.status_code = error.status_code
    return response


@exercises_api_bp.post("/")
def create_exercise():
    """
    create new exercise

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
        abort(HTTPStatus.NOT_FOUND, _id)

    data = request.get_json()
    exercise_data.update(data)
    try:
        exercise = ExerciseModel.parse_obj(exercise_data)
    except ValidationError as error:
        raise InvalidPayload("bad request: invalid exercise payload", error) from None

    result = app.db.exercises.update_one({"_id": _id}, exercise.model_dump(by_alias=True, exclude={"id"}))

    return jsonify(message="exercise updated successfully", acknowledged=result.acknowledged,
                   result=result.raw_result), HTTPStatus.OK


@exercises_api_bp.get("/<string:_id>/")
def get_exercise(_id):
    exercise_data = app.db.exercises.find_one({"_id": _id})
    if exercise_data is None:
        abort(HTTPStatus.NOT_FOUND, _id)

    return jsonify(exercise_data), HTTPStatus.OK


@exercises_api_bp.delete("/<string:_id>/")
def delete_exercise(_id):
    result = app.db.exercises.delete_one({"_id": _id})
    if result.deleted_count == 0:
        abort(HTTPStatus.NOT_FOUND, _id)

    return jsonify(message="Exercise deleted successfully.", acknowlegded=result.acknowledged), HTTPStatus.OK
