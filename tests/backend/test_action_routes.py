

import datetime
import json
import unittest.mock
from http import HTTPStatus
from pprint import pprint

import pytest
from dotenv import load_dotenv
from pymongo.synchronous.collection import Collection


from blueprints.backends.actions_api import ActionModel, ActionType
from models import TrainingModel

load_dotenv()
from app import create_app


# docker run -p 27017:27017 --name mongo_trainings --pull missing mongo:latest


@pytest.fixture(autouse=True)
def app_dict():

    # create app with test settings
    app = create_app()
    app.config.update({
        "TESTING": True
    })

    with app.app_context():
        yield {"app": app, 'db': app.db}

    # post test teardown

@pytest.fixture()
def client(app_dict):

    app = app_dict['app']
    client = app.test_client()

    database_operations.add_some_exercises()
    database_operations.add_some_trainings()
    database_operations.add_exercises_to_first_training()

    yield client

    database_operations.clear_mongo_db()

@pytest.fixture()
def item_ids(app_dict):
    """returns a dictionary of all ids of the exercises and trainings loaded into the db"""

    db = app_dict["db"]

    return {"exercises": [v["_id"] for v in db.exercises.find({})],
            "trainings": [v["_id"] for v in db.trainings.find({})]
            }

def test_action_reorder(client, app_dict, item_ids):
    """tests the reorder action."""
    db = app_dict['db']

    action = ActionModel(action_type=ActionType.reorder, position=0, arg="1")
    training_id = item_ids["trainings"][0]

    training_pre = TrainingModel(**db.trainings.find_one({"_id": training_id}))

    response = client.post(f'api/actions/{training_id}/',
                           json=action.model_dump(),
                           headers={"Content-Type": "Application/json"})


    assert response.status_code == HTTPStatus.OK, "status 200 expected for read exercise"

    training_post = TrainingModel(**db.trainings.find_one({"_id": training_id}))

    assert training_pre.exercises != training_post.exercises
    assert training_pre.exercises[0] == training_post.exercises[1]


def test_action_remove(client, app_dict, item_ids):
    """tests the remove exercise action."""
    db = app_dict['db']

    action = ActionModel(action_type=ActionType.remove, position=0)
    training_id = item_ids["trainings"][0]

    training_pre = TrainingModel(**db.trainings.find_one({"_id": training_id}))

    response = client.post(f'api/actions/{training_id}/',
                           json=action.model_dump(),
                           headers={"Content-Type": "Application/json"})


    assert response.status_code == HTTPStatus.OK, "status 200 expected for read exercise"

    training_post = TrainingModel(**db.trainings.find_one({"_id": training_id}))

    assert training_post.exercises == training_pre.exercises[1:], "expected first exercise to be removed"


def test_action_add(client, app_dict, item_ids):
    """tests the add exercise action."""
    db = app_dict['db']

    # get a training
    training_id = item_ids["trainings"][0]
    training_pre = TrainingModel(**db.trainings.find_one({"_id": training_id}))

    # get an exercise id
    new_exercise_id = item_ids["exercises"][3]

    action = ActionModel(action_type=ActionType.add, position=0, arg=new_exercise_id)

    response = client.post(f'api/actions/{training_id}/',
                           json=action.model_dump(),
                           headers={"Content-Type": "Application/json"})


    assert response.status_code == HTTPStatus.OK, "status 200 expected for read exercise"

    training_post = TrainingModel(**db.trainings.find_one({"_id": training_id}))

    assert training_post.exercises == [new_exercise_id] + training_pre.exercises, \
        "expected new exercise at position 0"

