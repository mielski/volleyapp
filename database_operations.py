import datetime
import os
import uuid
from dataclasses import asdict

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection

from models import TrainingModel, Exer
load_dotenv()
from app import app


# docker run -p 27017:27017 --name mongo_trainings --pull missing mongo:latest

trainings: Collection = app.db.trainings
def delete_all():
    trainings.delete_many({})


def fetch_all():
    for entry in trainings.find({}):
        print(entry)


def add_some_trainings():
    """Adds two trainings to the trainings collection"""

    tm1 = TrainingModel(title="Passing - houding voeten", date="2024-09-20", rating=1,
                        description="Doel: oefenen op het klaarstaan voor de bal met juiste houding voetenwerk.")
    tm2 = TrainingModel(title="Passing - beweging naar bal", date="2024-09-27", rating=1,
                        description="Doel: oefenen op balbaanbehoordeling en achter de bal komen")

    trainings.insert_one(tm1.model_dump(by_alias=True))
    trainings.insert_one(tm2.model_dump(by_alias=True))

if __name__ == '__main__':

    delete_all()
    add_some_trainings()
    fetch_all()
