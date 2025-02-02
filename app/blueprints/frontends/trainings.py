"""
Routes for the trainings frontend, such as viewing all the trainings.

These endpoints rely on the trainings templates.
"""
from typing import cast

from flask import Blueprint, current_app, render_template, abort, url_for, redirect, flash

from app.forms import TrainingFormDetailed, TrainingForm
from app.models import TrainingModel, ExerciseModel
from app.training_app import MyTrainingsApp
from app.auth import login_required

trainings_bp = Blueprint('trainings', __name__, template_folder="templates")

app = cast(MyTrainingsApp, current_app)


def load_exercises(training: TrainingModel) -> list[ExerciseModel]:

    exercise_ids = training.exercises
    exercises = [ExerciseModel(**app.db.exercises.find_one(id_)) for id_ in exercise_ids]
    for exercise in exercises:
        exercise.image_blob_urls = [app.blob_url_builder.get_url(name) for name in exercise.image_blob_names]
    return exercises


def get_training_data(_id) -> dict:
    """Loads data from id and returns abort if the id cannot be found.

    This will at some point become a function related to database operations."""
    training_data = app.db.trainings.find_one({"_id": _id})
    if training_data is None:
        abort(404, "the requested id does not exist")
    return training_data

@trainings_bp.route('/trainings')
def view_trainings():

    training_collection = app.db.trainings.find({})

    trainings = [TrainingModel(**training_item) for training_item in training_collection]
    return render_template("trainings/trainings.html",
                           trainings=trainings)
@trainings_bp.route("/training/<string:_id>/view", methods=["GET"])
def training_details_view(_id):
    """endpoint to view the training details in a well formatted html."""

    # load the item
    training_data = get_training_data(_id)
    training = TrainingModel(**training_data)
    exercises = load_exercises(training)

    # load the exercises used in the training


    # render the item
    return render_template("trainings/training_details_view.html",
                           training=training, exercises=exercises)


@trainings_bp.route("/training/<string:_id>/edit", methods=["GET", "POST", "DELETE"])
@login_required
def training_details_edit(_id):
    """endpoint to edit the training details in a well formatted html."""

    training = get_training_data(_id)

    form = TrainingFormDetailed(**training)
    if form.validate_on_submit():
        training = TrainingModel(**form.data)

        #add training to database
        training_dict = training.model_dump(by_alias=True)
        training_dict.pop("_id")
        app.db.trainings.update_one({"_id": _id}, {"$set": training_dict})
        flash("training edit completed", "")
        return redirect(url_for("trainings.training_details_view", _id=_id))

    # render the item
    return render_template("trainings/training_details_edit.html",
                           form=form, title="Edit Training")




@trainings_bp.route("/training/<string:_id>/delete", methods=["POST"])
@login_required
def training_details_delete(_id):
    """endpoint to delete the training."""

    training_item = app.db.trainings.find_one({"_id": _id})
    if training_item is None:
        abort(404, "the requested training does not exist")

    flash(f"The training '{training_item.get("title")}' has been deleted")
    app.db.trainings.delete_one({"_id": _id})

    return redirect(url_for("trainings.view_trainings"), code=302)


@trainings_bp.route('/trainings/new', methods=["GET", "POST"])
@login_required
def create_training():
    """raises a form to create a new training"""
    form = TrainingForm()
    if form.validate_on_submit():
        training = TrainingModel(rating=0, **form.data)

        #add training to database
        training_dict = training.model_dump(by_alias=True)
        app.db.trainings.insert_one(training_dict)

        flash("new training created")
        return redirect(url_for("trainings.view_trainings"))
    return render_template("trainings/training_new.html",
                           form=form, title="Add Training")
