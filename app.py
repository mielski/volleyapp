from flask import Flask, flash, url_for, redirect, render_template
from flask_bootstrap import Bootstrap5
import flask_wtf
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
app.secret_key = 'dev'

bootstrap = Bootstrap5(app)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/form', methods=["GET", "POST"])
def test_form():
    form = HelloForm()
    if form.validate_on_submit():
        flash("Form validated!")
        return redirect(url_for("hello_world"))
    return render_template("form.html",
                           form=form)

class HelloForm(flask_wtf.FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 150)])
    remember = BooleanField('Remember me')
    submit = SubmitField()


if __name__ == '__main__':
    app.run()
