import base64
import os
from logging import basicConfig, INFO, getLogger
from pathlib import Path

import flask
import flask_login
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from flask import render_template, request
from flask_bootstrap import Bootstrap5
from pymongo import MongoClient

from app.blueprints.frontends.trainings import trainings_bp
from app.blueprints.frontends.exercises import exercises_bp
from app.training_app import MyTrainingsApp
from app.blueprints.backends.exercises_api import exercises_api_bp
from app.blueprints.backends.actions_api import actions_api_bp
from app.storage import BlobStorageUrlBuilder
from app.forms import LoginForm
from models import ExerciseModel

CONTAINERNAME = "volleyimages"

basicConfig(level=INFO)

logger = getLogger(__name__)


def b64encode(data):
    return base64.b64encode(data).decode('utf-8')


class User(flask_login.UserMixin):

    pass


def create_app():
    """create the volleybal exercise application."""
    app = MyTrainingsApp(__name__)
    app.secret_key = 'dev'

    load_dotenv(".")
    app.db = MongoClient(os.environ["MONGO_URI"])['trainings_database']
    app.db.trainings = app.db['trainings']
    app.db.exercises = app.db['exercises']
    app.filelist = {} # temporary

    if os.getenv("STORAGE_CONNECTION_STRING"):
        storage_client = BlobServiceClient.from_connection_string(os.getenv("STORAGE_CONNECTION_STRING"))
        app.blob_container = storage_client.get_container_client(CONTAINERNAME)
        app.blob_url_builder = BlobStorageUrlBuilder(storage_client, CONTAINERNAME)
    else:
        logger.warning("no blob service connected, loading of images disabled")
        app.blob_container = None
        app.blob_url_builder = None

    # Register frontend blueprints
    app.register_blueprint(trainings_bp)
    app.register_blueprint(exercises_bp)

    #register backend blueprints
    app.register_blueprint(exercises_api_bp)
    app.register_blueprint(actions_api_bp)

    bootstrap = Bootstrap5(app)
    app.jinja_env.filters['b64encode'] = b64encode

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(email):
        if email != os.getenv("AUTH_EMAIL"):
            return

        user = User()
        user.id = email
        return user

    @login_manager.request_loader
    def request_loader(request):
        email = request.form.get('email')
        if email  != os.getenv("AUTH_EMAIL"):
            return

        user = User()
        user.id = email
        return user

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if flask.request.method == 'GET':
            return '''
                   <form action='login' method='POST'>
                    <input type='text' name='email' id='email' placeholder='email'/>
                    <input type='password' name='password' id='password' placeholder='password'/>
                    <input type='submit' name='submit'/>
                   </form>
                   '''

        email = flask.request.form['email']
        if email in users and flask.request.form['password'] == users[email]['password']:
            user = User()
            user.id = email
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('protected'))

        return 'Bad login'
    @app.route('/')
    def index():  # immediate redirect to view

        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule}")

        return render_template("index.html")

    @app.route("/testpage", methods=["GET", "POST"])
    def testpage():
        """page used during development"""

        form = LoginForm()

        if form.validate_on_submit():
            email = form.email
            pwd = form.password

            if email == os.getenv("AUTH_EMAIL") and pwd == os.getenv("AUTH_PWD"):
                login_manager.
        return render_template("testpage.html",form=form)
    return app