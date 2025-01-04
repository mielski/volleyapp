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
    add = "add"
    remove = "remove"
    append = "append"


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
    print(data)
    try:
        action = ActionModel.parse_obj(data)
    except ValidationError as error:
        return jsonify({
            "status": "error",
            "message": "Invalid action payload",
            "error_code": 400,
            "data": error.errors()
        })
    print(action)
    exercises = training.exercises
    if action.action_type == ActionType.reorder:
        # reorder the position of two exercises
        pos1 = action.position
        try:
            pos2 = int(action.arg)
        except TypeError:
            return bad_request_error("error in 'arg' parameter: unable to convert into integer as new position.")
        print("reordering!")
        exercises.insert(pos2, exercises.pop(pos1))

    elif action.action_type in (ActionType.add, ActionType.append):
        # add a new exercise to target position in the list
        new_exercise_id = action.arg
        if not app.db.exercises.find({"_id": new_exercise_id}):
            return bad_request_error("exercise id does not exist (provided in request via arg).")
        if action.action_type == ActionType.append:
            exercises.append(new_exercise_id)
        else:
            # else, action type = add and more sanity check required
            if action.position > len(exercises):
                return bad_request_error("position parameter exceeds lengths of exercises.")

            exercises.insert(action.position, new_exercise_id)
    elif action.action_type == ActionType.remove:
        # remove an exercise by position
        if action.position > len(exercises) - 1:
            return bad_request_error("position parameter exceeds numer of exercises available.")
        exercises.pop(action.position)


    new_data = training.model_dump(by_alias=True, exclude="id")
    app.db.trainings.update_one({"_id": training_id}, {"$set": new_data})

    return jsonify({
        "status": "success",
        "message": "Action completed successfully",
    }), 200


def bad_request_error():
    return jsonify({
        "status": "error",
        "message": "Invalid arg parameters type, unable to convert to integer",
        "error_code": 400
    }), HTTPStatus.BAD_REQUEST

