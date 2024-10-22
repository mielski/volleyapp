import os

import pymongo.database
from dotenv import load_dotenv
from flask import Flask, flash, url_for, redirect, render_template, abort, Request, request
from flask_bootstrap import Bootstrap5

from pymongo import MongoClient

from blueprints.trainings.routes import trainings_bp
from myflask import MyTrainingsApp

app = MyTrainingsApp(__name__)
app.secret_key = 'dev'

bootstrap = Bootstrap5(app)

# setup mongo client and database
load_dotenv(".")
app.db = MongoClient(os.environ["MONGO_SERVER"])['trainings_database']
app.db.trainings = app.db['trainings']

app.register_blueprint(trainings_bp)


@app.route('/')
def index():  # immediate redirect to training
    return redirect(url_for("trainings.view_trainings"))

@app.route('/exercices')
def view_exercises():

    return render_template("exercises.html",
                           title="Under construction")



if __name__ == '__main__':
    app.run()
