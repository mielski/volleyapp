import os

from dotenv import load_dotenv
from flask import redirect, url_for
from flask_bootstrap import Bootstrap5
from pymongo import MongoClient

from app.blueprints.frontends.trainings import trainings_bp
from app.blueprints.frontends.exercises import exercises_bp
from app.training_app import MyTrainingsApp



def create_app():
    """create the volleybal exercise application."""
    app = MyTrainingsApp(__name__)
    app.secret_key = 'dev'

    load_dotenv(".")
    app.db = MongoClient(os.environ["MONGO_SERVER"])['trainings_database']
    app.db.trainings = app.db['trainings']
    app.db.exercises = app.db['exercises']


    # Register blueprints
    app.register_blueprint(trainings_bp)
    app.register_blueprint(exercises_bp)

    bootstrap = Bootstrap5(app)

    @app.route('/')
    def index():  # immediate redirect to view

        exercise = app.db.exercises.find_one()

        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule}")
        return redirect(url_for("exercises.view_all_exercises"))
        return "Hello world"

    return app
