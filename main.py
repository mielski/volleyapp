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
def index():  # immediate redirect to training
    return redirect(url_for("edit_exercise"))

@app.route('/view_exercices')
def view_exercises():

    exercises = [VolleyballExercise(**exercise) for exercise in app.db.exercises.find({})]
    return render_template("exercises/view_exercises.html",
                           title="Under construction", exercises=exercises)

@app.route('/exercices')
def edit_exercise():

    exercise = app.db.exercises.find_one({})
    exercise = VolleyballExercise(**exercise)

    form = VolleyballExerciseForm.from_exercise(exercise)

    return render_template('exercises/edit.html', exercise=exercise, form=form)

if __name__ == '__main__':
    app.run()
