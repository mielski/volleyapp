from typing import cast
from http import HTTPStatus

from flask import abort, Blueprint, current_app, jsonify, make_response, request
from pydantic import ValidationError

from app.errors import InvalidPayload
from app.models import TrainingModel
from app.training_app import MyTrainingsApp

trainings_api_bp = Blueprint('trainings_api', __name__, url_prefix="/api/trainings")

app = cast(MyTrainingsApp, current_app)


@trainings_api_bp.errorhandler(404)
def not_found(error):
    response = jsonify(
        {"status": 404,
         "error": "Not Found",
         "message": f"The requested resource for id '{error.description}' was not found."}
    )
    return response, HTTPStatus.NOT_FOUND


@trainings_api_bp.errorhandler(InvalidPayload)
def handle_invalid_payload(error: InvalidPayload):
    response = jsonify(error.error_list)
    response.status_code = error.status_code
    return response


@trainings_api_bp.post("/")
def create_training():
    """
    create new training

    :return: json with following keys:
    - acknowlegded: true or false based whether created was successful
    - id: the id of the new training
    """

    data = request.get_json()
    try:
        training = TrainingModel.parse_obj(data)
    except ValidationError as error:
        raise InvalidPayload("bad request: invalid training payload", error) from None
    result = app.db.trainings.insert_one(training.model_dump(by_alias=True))
    return jsonify({"acknowledged": result.acknowledged, "id_": result.inserted_id}), HTTPStatus.CREATED


@trainings_api_bp.get("/")
def get_trainings():
    """Get all trainings as a list"""

    data = [training for training in app.db.trainings.find()]
    return jsonify(data), HTTPStatus.OK


@trainings_api_bp.put("/<string:_id>/")
def update_training(_id):
    """update the information of the training"""

    training_data = dict(app.db.trainings.find_one({"_id": _id}))
    if training_data is None:
        abort(HTTPStatus.NOT_FOUND, _id)

    data = request.get_json()
    training_data.update(data)
    try:
        training = TrainingModel.parse_obj(training_data)
    except ValidationError as error:
        raise InvalidPayload("bad request: invalid training payload", error) from None

    result = app.db.trainings.update_one({"_id": _id}, training.model_dump(by_alias=True, exclude={"id"}))

    return jsonify(message="training updated successfully", acknowledged=result.acknowledged,
                   result=result.raw_result), HTTPStatus.OK


@trainings_api_bp.get("/<string:_id>/")
def get_training(_id):
    training_data = app.db.trainings.find_one({"_id": _id})
    if training_data is None:
        abort(HTTPStatus.NOT_FOUND, _id)

    return jsonify(training_data), HTTPStatus.OK


@trainings_api_bp.delete("/<string:_id>/")
def delete_training(_id):
    result = app.db.trainings.delete_one({"_id": _id})
    if result.deleted_count == 0:
        abort(HTTPStatus.NOT_FOUND, _id)

    return jsonify(message="training deleted successfully.", acknowlegded=result.acknowledged), HTTPStatus.OK
