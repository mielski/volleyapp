import datetime
import unittest.mock

import pytest
from dotenv import load_dotenv
from pymongo.synchronous.collection import Collection

import app.blueprints.trainings.routes
from app.blueprints.trainings import load_exercises
from app.models import TrainingModel

load_dotenv()
from main import app


# docker run -p 27017:27017 --name mongo_trainings --pull missing mongo:latest

trainings: Collection = app.db.trainings
exercises: Collection = app.db.exercises

@pytest.fixture(autouse=True)
def set_app_context():
    with app.app_context():
        yield

@unittest.mock.patch.object(exercises, "find_one")
def test_load_exercises(mock_exercises_col):

    training = TrainingModel(title="test_training",
                             date=datetime.datetime(2024, 12, 31),
                             exercises=["1", "2"])

    mock_exercises_col.side_effect = [
        {"_id": "1",
         "title": "test",
         "difficulty_level": "Beginner",
         "duration": 5,
         },
        {"_id": "2",
         "title": "test2",
         "difficulty_level": "Beginner",
         "duration": 10,
         }
    ]

    training_exercises = load_exercises(training)
    assert training_exercises[0].id == "1"
    assert training_exercises[1].id == "2"

