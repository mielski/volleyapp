import logging
from typing import cast

from azure.storage.blob import ContentSettings
from flask import abort, Blueprint, current_app, redirect, url_for, render_template, request, flash

from app.forms import VolleyballExerciseForm
from app.models import ExerciseModel
from app.training_app import MyTrainingsApp
from app.auth import login_required

exercises_bp = Blueprint('exercises', __name__, template_folder="templates")

app = cast(MyTrainingsApp, current_app)

logger = logging.getLogger(__name__)

def get_exercise_data(_id) -> dict:
    """Loads exercise dictionary from database returns abort if the id cannot be found.

    This will at some point become a function related to database operations."""
    exercise_data = app.db.exercises.find_one({"_id": _id})
    if exercise_data is None:
        abort(404, "the requested exercise id does not exist")
    return exercise_data

@exercises_bp.route('/exercises/view_exercises')
def view_all_exercises():

    exercises = [ExerciseModel(**exercise) for exercise in app.db.exercises.find({})]

    training_id = request.args.get("training_id")
    return render_template("exercises/view_exercises.html",
                           title="View Exercises", exercises=exercises,
                           training_id=training_id)

@exercises_bp.route('/exercises/<string:_id>/view')
def view_exercise(_id):

    exercise_data = get_exercise_data(_id)
    exercise = ExerciseModel(**exercise_data)

    exercise.image_blob_urls = [app.blob_url_builder.get_url(name) for name in exercise.image_blob_names]
    return render_template('exercises/view.html', exercise=exercise)


@exercises_bp.route('/exercises/<string:_id>/edit', methods=["GET", "POST"])
@login_required
def edit_exercise(_id):
    """endpoint for form to edit an exercise and add/remove images."""
    form = VolleyballExerciseForm()

    if form.validate_on_submit():

        # 1 - do actions with input about blob images
        # 1a ) remove indicated images via blobs_to_delete
        blobs_to_remove = request.form["blobs_to_delete"]
        if blobs_to_remove != "":
            blobs_to_remove = blobs_to_remove.split(",")
            print("files to remove: ", blobs_to_remove)
            app.blob_container.delete_blobs(*blobs_to_remove)
            for blobname in blobs_to_remove:
                # exercise.image_blob_names.remove(filename)
                app.db.exercises.update_one({"_id": _id}, {"$pull": {"image_blob_names": blobname}})

        # 1b) add new images set via the new_images widget
        filelist = request.files.getlist("new_images")
        if filelist != [""]:

            logger.info(f"got {len(filelist)} files")
            for file_ in filelist:
                file_data = file_.read()
                mime_type = file_.mimetype
                blobname = file_.filename
                if blobname == "":
                    continue
                logger.info(f"storing blob {blobname} to storage")
                app.blob_container.upload_blob(name=blobname, data=file_data,
                                               content_settings=ContentSettings(content_type=mime_type))
                app.db.exercises.update_one({"_id": _id}, {"$push": {"image_blob_names": blobname}})

        # 2) load the exercise data from the remaining form and update db.
        exercise = ExerciseModel(**form.data)
        exercise_dict = exercise.model_dump(by_alias=True, exclude={"id", "image_blob_names"})
        app.db.exercises.update_one({"_id": _id}, {"$set": exercise_dict})
        flash("succes!")
        return redirect(url_for("exercises.view_all_exercises"))

    else:
        exercise_data = get_exercise_data(_id)
        exercise = ExerciseModel(**exercise_data)
        app.blob_url_builder.add_urls(exercise)
        form = VolleyballExerciseForm.from_exercise(exercise)
        return render_template('exercises/edit.html', exercise=exercise, form=form)

@exercises_bp.route('/exercises/new_exercise', methods=["GET", "POST"])
@login_required
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

