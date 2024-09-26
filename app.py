from flask import Flask, flash, url_for, redirect, render_template
from flask_bootstrap import Bootstrap5
import flask_wtf
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

from forms import TrainingForm

app = Flask(__name__)
app.secret_key = 'dev'

bootstrap = Bootstrap5(app)

@app.route('/')
def index():  # put application's code here
    return render_template("index.html", title="Hello")

@app.route('/trainings', methods=["GET", "POST"])
def trainings():
    form = HelloForm()
    if form.validate_on_submit():
        flash("Form validated!")
        return redirect(url_for("index"))
    return render_template("trainings.html",
                           form=form, title="Trainings")
@app.route('/trainings/new', methods=["GET", "POST"])
def create_training():
    """raises a form to create a new training"""
    form = TrainingForm()
    if form.validate_on_submit():
        flash("Form validated!")
        return redirect(url_for("trainings"))
    return render_template("training_base.html",
                           form=form, title="Add Training")
@app.route('/forms', methods=["GET", "POST"])
def example_forms():
    form = HelloForm()
    if form.validate_on_submit():
        flash("Form validated!")
        return redirect(url_for("index"))
    return render_template("form.html",
                           form=form, title="Form Example")

class HelloForm(flask_wtf.FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 150)])
    remember = BooleanField('Remember me')
    submit = SubmitField()


if __name__ == '__main__':
    app.run()
