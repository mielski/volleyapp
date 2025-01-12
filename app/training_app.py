from flask import Flask
from pymongo.synchronous.collection import Collection
from storage import BlobStorageUrlBuilder

class TrainingMongoClient:

    exercises: Collection
    trainings: Collection


class MyTrainingsApp(Flask):
    db: TrainingMongoClient
    blob_url_builder: BlobStorageUrlBuilder


