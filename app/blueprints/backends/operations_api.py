"""endpoints to update exercise information inside trainings.

This is still experimental"""
from enum import Enum
from typing import cast, Annotated
from http import HTTPStatus

from flask import abort, Blueprint, current_app, jsonify, make_response, request
from pydantic import ValidationError, BaseModel, Field, conint

from app.errors import InvalidPayload
from app.models import TrainingModel, ExerciseModel
from app.training_app import MyTrainingsApp

actions_api_bp = Blueprint('actions_api_bp', __name__, url_prefix="/api/actions")

app = cast(MyTrainingsApp, current_app)


class ActionType(str, Enum):
    reorder = "reorder"


class ActionModel(BaseModel):

    action_type: ActionType
    position: Annotated[int, Field(title="the position of the exercise to act on", ge=0)]
    id: str = Field(default="")
    arg: str = Field(default="", title="room for additional arguments that some actions require")


@actions_api_bp.errorhandler(404)
def not_found(error):
    response = jsonify(
        {"status": 404,
         "error": "Not Found",
         "message": f"The requested resource for id '{error.description}' was not found."}
    )
    return response, HTTPStatus.NOT_FOUND


@actions_api_bp.errorhandler(InvalidPayload)
def handle_invalid_payload(error: InvalidPayload):
    response = jsonify(error.error_list)
    response.status_code = error.status_code
    return response


@actions_api_bp.post("/<string:training_id>/")
def apply_action(training_id):
    """
    experimental api to apply high level actions to the target training

    supported actions:
    - reorder: change the position of an item in the exercise list.
    - that's all for now, this list will grow.
    """
    training_data = dict(app.db.trainings.find_one({"_id": training_id}))
    if training_data is None:
        abort(HTTPStatus.NOT_FOUND, training_id)
    training = TrainingModel(**training_data)


    data = request.get_json()
    try:
        action = ActionModel.parse_raw(data)
    except ValidationError as error:
        raise InvalidPayload("bad request: invalid action payload", error) from None

    if action.action_type == ActionType.reorder:
        # reorder the position of two exercises
        exercises = training.exercises
        pos1 = action.position
        try:
            pos2 = int(action.arg)
        except TypeError:
            return jsonify({
                "message": "invalid action parameters, requres position and integer arg"
            }), HTTPStatus.BAD_REQUEST
        print("reordering!")
        exercises.insert(pos2, exercises.pop(pos1))
        new_data = training.model_dump(by_alias=True, exclude="id")
        app.db.trainings.update_one({"_id": training_id}, {"$set": new_data})
    return jsonify({"message": "action completed"}), 200
