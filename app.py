import os

import pymongo.database
from dotenv import load_dotenv
from flask import Flask, flash, url_for, redirect, render_template, abort
from flask_bootstrap import Bootstrap5
import flask_wtf
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

from forms import TrainingForm, TrainingFormDetailed
from models import TrainingModel

app = Flask(__name__)
app.secret_key = 'dev'

bootstrap = Bootstrap5(app)

# setup mongo client and database
load_dotenv(".")
from pymongo import MongoClient

# Create an in-memory MongoDB client

# Access a test database and collection
app.db = MongoClient(os.environ["MONGO_SERVER"])['trainings_database']
app.db.trainings = app.db['trainings']

@app.route('/')
def index():  # put application's code here
    return render_template("index.html", title="Hello")

@app.route('/trainings')
def view_trainings():

    training_collection = app.db.trainings.find({})

    trainings = [TrainingModel(**training_item) for training_item in training_collection]

    return render_template("trainings.html",
                           trainings=trainings, title="Trainings")

@app.route("/training/<string:id_>/view", methods=["GET"])
def training_details_view(id_):
    """endpoint to view the training details in a well formatted html."""

    # load the item
    training_item = app.db.trainings.find_one({"_id": id_})
    if training_item is None:
        abort(404, "the requested id does not exist")
    training = TrainingModel(**training_item)

    # render the item
    return render_template("training_details_view.html",
                           training=training, title="View Training")
@app.route("/training/<string:id_>/edit", methods=["GET","POST"])
def training_details_edit(id_):
    """endpoint to edit the training details in a well formatted html."""

    training_item = app.db.trainings.find_one({"_id": id_})
    if training_item is None:
        abort(404, "the requested id does not exist")

    form = TrainingFormDetailed(**training_item)
    if form.validate_on_submit():
        training = TrainingModel(**form.data)

        #add training to database
        training_dict = training.model_dump(by_alias=True)
        app.db.trainings.update_one({"id_": id_}, training_dict)
        return redirect(url_for("training_details_view", id_=id_))

    # render the item
    return render_template("training_details_edit.html",
                           form=form, title="Edit Training")

@app.route('/trainings/new', methods=["GET", "POST"])
def create_training():
    """raises a form to create a new training"""
    form = TrainingForm()
    if form.validate_on_submit():
        training = TrainingModel(**form.data)

        #add training to database
        training_dict = training.model_dump(by_alias=True)
        app.db.trainings.insert_one(training_dict)

        return redirect(url_for("view_trainings"))
    return render_template("training_new.html",
                           form=form, title="Add Training")



if __name__ == '__main__':
    app.run()
