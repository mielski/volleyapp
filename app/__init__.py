import os

from dotenv import load_dotenv
from flask import redirect, url_for, jsonify
from flask_bootstrap import Bootstrap5
from pymongo import MongoClient

from app.blueprints.frontends.trainings import trainings_bp
from app.blueprints.frontends.exercises import exercises_bp
from app.training_app import MyTrainingsApp
from blueprints.backends.exercises_api import exercises_api_bp
from blueprints.backends.actions_api import actions_api_bp


def create_app():
    """create the volleybal exercise application."""
    app = MyTrainingsApp(__name__)
    app.secret_key = 'dev'

    load_dotenv(".")
    app.db = MongoClient(os.environ["MONGO_SERVER"])['trainings_database']
    app.db.trainings = app.db['trainings']
    app.db.exercises = app.db['exercises']


    # Register frontend blueprints
    app.register_blueprint(trainings_bp)
    app.register_blueprint(exercises_bp)

    #register backend blueprints
    app.register_blueprint(exercises_api_bp)
    app.register_blueprint(actions_api_bp)

    bootstrap = Bootstrap5(app)

    @app.route('/')
    def index():  # immediate redirect to view

        exercise = app.db.exercises.find_one()

        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule}")
        return redirect(url_for("exercises.view_all_exercises"))


    return app
