from flask import Flask
from pymongo import MongoClient


class MyTrainingsApp(Flask):
    db: MongoClient
