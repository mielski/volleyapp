import os

from dotenv import load_dotenv
from flask_bootstrap import Bootstrap5

from pymongo import MongoClient

from app.blueprints.trainings.routes import trainings_bp

from flask import Flask, abort, redirect, url_for, render_template

from app.forms import VolleyballExerciseForm
from app.models import ExerciseModel
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
    # app.register_blueprint(frontend)
    # app.register_blueprint(backend)

    bootstrap = Bootstrap5(app)

    def get_exercise_data(_id) -> dict:
        """Loads exercise dictionary from database returns abort if the id cannot be found.

        This will at some point become a function related to database operations."""
        exercise_data = app.db.exercises.find_one({"_id": _id})
        if exercise_data is None:
            abort(404, "the requested exercise id does not exist")
        return exercise_data

    @app.route('/')
    def index():  # immediate redirect to view

        exercise = app.db.exercises.find_one()

        return redirect(url_for("view_all_exercises"))

    @app.route('/exercises/view_exercises')
    def view_all_exercises():

        exercises = [ExerciseModel(**exercise) for exercise in app.db.exercises.find({})]
        return render_template("exercises/view_exercises.html",
                               title="View Exercises", exercises=exercises)

    @app.route('/exercises/<string:_id>/view')
    def view_exercise(_id):

        exercise_data = get_exercise_data(_id)
        exercise = ExerciseModel(**exercise_data)

        return render_template('exercises/view.html', exercise=exercise)

    @app.route('/exercises/<string:_id>/edit', methods=["GET", "POST"])
    def edit_exercise(_id):

        form = VolleyballExerciseForm()

        if form.validate_on_submit():
            # ran when post method is successful -> update data about exercise from form data
            exercise = ExerciseModel(**form.data)
            exercise_dict = exercise.model_dump(by_alias=True)
            exercise_dict.pop("_id")
            app.db.exercises.update_one({"_id": _id}, {"$set": exercise_dict})
            return redirect(url_for("view_all_exercises"))

        else:
            exercise_data = get_exercise_data(_id)
            exercise = ExerciseModel(**exercise_data)
            form = VolleyballExerciseForm.from_exercise(exercise)
            return render_template('exercises/edit.html', exercise=exercise, form=form)

    @app.route('/new_exercise', methods=["GET", "POST"])
    def new_exercise():
        """Creates a new exercise and adds it to the database on form submit."""

        form = VolleyballExerciseForm()

        if form.validate_on_submit():
            exercise = ExerciseModel(**form.data)

            # add exercise to database
            exercise_dict = exercise.model_dump(by_alias=True)
            app.db.exercises.insert_one(exercise_dict)
            return redirect(url_for("view_all_exercises"))

        else:
            return render_template('exercises/new.html', exercise=None, form=form, title="new exercise")

    return app
