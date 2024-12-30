

import datetime
import json
import unittest.mock
from pprint import pprint

import pytest
from dotenv import load_dotenv
from pymongo.synchronous.collection import Collection

import app.blueprints.frontends.trainings
import database_operations
from blueprints.backends.exercises_api import create_exercise
from flask import current_app

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

    database_operations.delete_all()


def test_create_exercise(client):

    data = {"title": "Hello World", "duration": 10, "difficulty_level": "Beginner"}
    response = client.post('/api/exercises/', json=data, headers={"Content-Type": "Application/json"})

    pprint(json.loads(response.text))
    pprint(response.status_code)
    pprint(response.status)


def test_read_exercises(client):

    response = client.get('/api/exercises/')