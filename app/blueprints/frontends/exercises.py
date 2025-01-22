from typing import cast

from flask import abort, Blueprint, current_app, redirect, url_for, render_template, request, session, flash

from app.forms import VolleyballExerciseForm
from app.models import ExerciseModel
from app.training_app import MyTrainingsApp

exercises_bp = Blueprint('exercises', __name__, template_folder="templates")

app = cast(MyTrainingsApp, current_app)


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
def edit_exercise(_id):

    form = VolleyballExerciseForm()

    if form.validate_on_submit():
        # ran when post method is successful -> update data about exercise from form data
        print(form.data)
        exercise = ExerciseModel(**form.data)
        exercise_dict = exercise.model_dump(by_alias=True)
        exercise_dict.pop("_id")
        print(exercise)
        if filelist := request.files.getlist("new_images"):
            for file_ in filelist:
                print(f"got {len(filelist)} files")
                file_data = file_.read()
                mime_type = file_.mimetype
                print(f"storing file to blob storage")
                app.filelist[file_.filename] = (file_data, mime_type)
        # app.db.exercises.update_one({"_id": _id}, {"$set": exercise_dict})
        print("delete images data: ", form.data.get("delete_images"))
        flash("succes!")
        return render_template('exercises/edit.html', exercise=exercise, form=form)
        return redirect(url_for("exercises.view_all_exercises"))

    else:
        exercise_data = get_exercise_data(_id)
        exercise = ExerciseModel(**exercise_data)
        app.blob_url_builder.add_urls(exercise)
        form = VolleyballExerciseForm.from_exercise(exercise)
        return render_template('exercises/edit.html', exercise=exercise, form=form)

@exercises_bp.route('/exercises/new_exercise', methods=["GET", "POST"])
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


