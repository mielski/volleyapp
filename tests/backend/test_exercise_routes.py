

import datetime
import json
import unittest.mock
from http import HTTPStatus
from pprint import pprint

import pytest
from dotenv import load_dotenv
from flask import url_for
from pymongo.synchronous.collection import Collection

import reset_test_data

load_dotenv()
from app import create_app


# docker run -p 27017:27017 --name mongo_trainings --pull missing mongo:latest


@pytest.fixture(autouse=True)
def app_dict():

    # create app with test settings
    app = create_app()
    app.config.update({
        "TESTING": True,
        "LOGIN_DISABLED": True,
    })

    with app.app_context():
        yield {"app": app, 'db': app.db}

    # post test teardown

@pytest.fixture()
def client(app_dict):

    app = app_dict['app']
    client = app.test_client()
    reset_test_data.clear_mongo_db()
    reset_test_data.add_some_exercises()
    reset_test_data.add_some_trainings()
    reset_test_data.add_exercises_to_first_training()

    yield client

    reset_test_data.clear_mongo_db()

@pytest.fixture()
def item_ids(app_dict):
    """returns a dictionary of all ids of the exercises and trainings loaded into the db"""

    db = app_dict["db"]

    return {"exercises": [v["_id"] for v in db.exercises.find({})],
            "trainings": [v["_id"] for v in db.trainings.find({})]
            }


def test_create_exercise(client):

    data = {"title": "Hello World", "duration": 10, "difficulty_level": "Beginner"}
    response = client.post('/api/exercises/', json=data, headers={"Content-Type": "Application/json"})

    assert response.status_code == HTTPStatus.CREATED
    assert response.json["acknowledged"] is True


def test_read_exercise(client, item_ids):
    """tests the read exercise api."""

    exercise_id = item_ids["exercises"][0]
    response = client.get(f'api/exercises/{exercise_id}/', headers={"Content-Type": "Application/json"})

    assert response.status_code == HTTPStatus.OK, "status 200 expected for read exercise"
    assert response.json["_id"] == exercise_id, "id of the returned exercise should match the requested one"


def test_read_exercise_wrong_id(client, item_ids):
    """tests the read exercise api if the id is not existing."""

    response = client.get(f'api/exercises/wrong_id_endpoint/', headers={"Content-Type": "Application/json"})

    assert response.status_code == HTTPStatus.NOT_FOUND, "status 404 expected for read exercise with wrong id"
    assert response.json["message"] == "The requested resource for id 'wrong_id_endpoint' was not found."


def test_read_exercises(client):

    response = client.get('/api/exercises/')
    assert response.status_code == HTTPStatus.OK


def test_delete_exercise(client, item_ids):

    exercise_id = item_ids['exercises'][0]
    response = client.delete(f"/api/exercises/{exercise_id}/", headers={"Content-Type": "Application/json"})

    assert response.status_code == HTTPStatus.OK
    assert response.json["message"] == "Exercise deleted successfully."

def test_delete_exercise_unauthorized(client, item_ids, app_dict, monkeypatch):

    app = app_dict["app"]
    monkeypatch.setitem(app.config, "LOGIN_DISABLED", False)
    exercise_id = item_ids['exercises'][0]
    response = client.delete(f"/api/exercises/{exercise_id}/", headers={"Content-Type": "Application/json"})

    with app.test_request_context():
        url = url_for("exercises_api.delete_exercise", _id=exercise_id, _external=True)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json == {"status": 401,
                             "message": "login required",
                             "error": "unauthorized",
                             "call": url}