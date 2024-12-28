import logging
import os

import pymongo.database
from dotenv import load_dotenv
from flask import Flask, flash, url_for, redirect, render_template, abort, Request, request
from flask_bootstrap import Bootstrap5

from pymongo import MongoClient

from blueprints.trainings.routes import trainings_bp
from app import MyTrainingsApp
from forms import VolleyballExerciseForm
from models import VolleyballExercise

app = MyTrainingsApp(__name__)
app.secret_key = 'dev'

bootstrap = Bootstrap5(app)

# setup mongo client and database
load_dotenv(".")
app.db = MongoClient(os.environ["MONGO_SERVER"])['trainings_database']
app.db.trainings = app.db['trainings']
app.db.exercises = app.db['exercises']

app.register_blueprint(trainings_bp)


@app.route('/')
def index():  # immediate redirect to view

    exercise = app.db.exercises.find_one()

    return redirect(url_for("view_exercise", _id=exercise["_id"]))

@app.route('/view_exercices')
def view_all_exercises():

    exercises = [VolleyballExercise(**exercise) for exercise in app.db.exercises.find({})]
    return render_template("exercises/view_exercises.html",
                           title="View Exercises", exercises=exercises)


@app.route('/exercices/<string:_id>/view')
def view_exercise(_id):

    exercise = app.db.exercises.find_one({"_id": _id})
    exercise = VolleyballExercise(**exercise)



    return render_template('exercises/view.html', exercise=exercise)

@app.route('/exercices/<string:_id>/edit', methods=["GET", "POST"])
def edit_exercise(_id):

    form = VolleyballExerciseForm()

    if form.validate_on_submit():
        # ran when post method is successful -> update data about exercise from form data
        exercise = VolleyballExercise(**form.data)
        exercise_dict = exercise.model_dump(by_alias=True)
        exercise_dict.pop("_id")
        app.db.exercises.update_one({"_id": _id}, {"$set": exercise_dict})
        return redirect(url_for("view_all_exercises"))

    else:
        exercise = app.db.exercises.find_one({"_id": _id})
        exercise = VolleyballExercise(**exercise)
        form = VolleyballExerciseForm.from_exercise(exercise)
        return render_template('exercises/edit.html', exercise=exercise, form=form)

@app.route('/new_exercise', methods=["GET", "POST"])
def new_exercise():
    """Creates a new exercise and adds it to the database on form submit."""

    form = VolleyballExerciseForm()

    if form.validate_on_submit():
        exercise = VolleyballExercise(**form.data)

        #add exercise to database
        exercise_dict = exercise.model_dump(by_alias=True)
        app.db.exercises.insert_one(exercise_dict)
        return redirect(url_for("view_all_exercises"))

    else:
        return render_template('exercises/new.html', exercise=None, form=form, title="new exercise")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run()
