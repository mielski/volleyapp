import os

import pymongo.database
from dotenv import load_dotenv
from flask import Flask, flash, url_for, redirect, render_template, abort, Request, request
from flask_bootstrap import Bootstrap5

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
def index():  # immediate redirect to training
    return redirect(url_for("view_trainings"))

@app.route('/trainings')
def view_trainings():

    training_collection = app.db.trainings.find({})

    trainings = [TrainingModel(**training_item) for training_item in training_collection]

    return render_template("trainings.html",
                           trainings=trainings, title="Trainings")

@app.route('/exercices')
def view_exercises():

    return render_template("exercises.html",
                           title="Under construction")
@app.route("/training/<string:_id>/view", methods=["GET"])
def training_details_view(_id):
    """endpoint to view the training details in a well formatted html."""

    # load the item
    training_item = app.db.trainings.find_one({"_id": _id})
    if training_item is None:
        abort(404, "the requested id does not exist")
    training = TrainingModel(**training_item)

    # render the item
    return render_template("training_details_view.html",
                           training=training, title="View Training")


@app.route("/training/<string:_id>/edit", methods=["GET","POST", "DELETE"])
def training_details_edit(_id):
    """endpoint to edit the training details in a well formatted html."""

    training_item = app.db.trainings.find_one({"_id": _id})
    if training_item is None:
        abort(404, "the requested id does not exist")

    form = TrainingFormDetailed(**training_item)
    if form.validate_on_submit():
        training = TrainingModel(**form.data)

        #add training to database
        training_dict = training.model_dump(by_alias=True)
        training_dict.pop("_id")
        app.db.trainings.update_one({"_id": _id}, {"$set": training_dict})
        return redirect(url_for("training_details_view", _id=_id))

    # render the item
    return render_template("training_details_edit.html",
                           form=form, title="Edit Training")


@app.route("/training/<string:_id>/delete", methods=["POST"])
def training_details_delete(_id):
    """endpoint to delete the training."""

    training_item = app.db.trainings.find_one({"_id": _id})
    if training_item is None:
        abort(404, "the requested training does not exist")

    flash(f"The training '{training_item.get("title")}' has been deleted")
    app.db.trainings.delete_one({"_id": _id})

    return redirect(url_for("view_trainings"), code=302)

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
