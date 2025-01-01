from flask import Flask
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection


class TrainingMongoClient:

    exercises: Collection
    trainings: Collection


class MyTrainingsApp(Flask):
    db: TrainingMongoClient


