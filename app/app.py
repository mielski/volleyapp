import base64
import datetime
import os
from logging import basicConfig, INFO, getLogger
from pathlib import Path

import flask
import flask_login
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from flask import render_template, request, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap5
from flask_login import current_user
from pymongo import MongoClient
from urllib3.util import parse_url

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

    @login_manager.unauthorized_handler
    def unauthorized_handler():
        """send on login on unauthorized request"""

        if request.blueprint.endswith("api"):
            # response for backend requests
            response = jsonify(
                {"status": 401,
                 "error": "unauthorized",
                 "message": "login required",
                 "call": f"{request.url}"
                 }
            )
            response.status_code = 401
            return response
        else:
            # response for frontend requests
            return redirect(url_for('login', next=request.url),)

    @app.route('/login', methods=['GET', 'POST'])
    def login():

        form = LoginForm()

        if form.validate_on_submit():
            email = form.email.data
            pwd = form.password.data

            if email == os.getenv("AUTH_EMAIL") and pwd == os.getenv("AUTH_PWD"):
                user = User()
                user.id = email
                flask_login.login_user(user, remember=True, duration=datetime.timedelta(minutes=15))
                if redirect_url := request.args.get("next"):
                    parsed_url = parse_url(redirect_url)
                    if parsed_url.netloc == request.host:
                        return redirect(redirect_url)

                return redirect(url_for("index"))
            else:
                flask.flash("login failed", "warning")

        return render_template("testpage.html", form=form)

    @app.route("/logout")
    def logout():
        """logs out user. On next page uses the following rules:
        - if redirect is not given, to go index
        - if ridirect is given but is protected endpoint, go to index
        - otherwise, to go redirect."""
        if current_user.is_authenticated:

            flask_login.logout_user()
            flask.flash("logout successfully")

        # check whether to use redirect
        redirect_url = request.args.get("next")
        if not redirect_url:
            return redirect(url_for("index"))

        # check if redirect is protected
        parsed_redirect = parse_url(redirect_url)
        adapter = app.url_map.bind('')
        try:
            endpoint, args = adapter.match(parsed_redirect.path)
            view_func = app.view_functions[endpoint]
            if hasattr(view_func, 'login_required'):
                logger.debug("redirect endpoint is protected -> redirect to index")
                return redirect(url_for("index"))
            else:
                return redirect(redirect_url)
                logger.debug("redirect url is public -> go to url")

        except Exception as e:
            logger.info("exception while matching redirect url with url map")
            logger.info(e)
        return redirect(url_for('index'))


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
            email = form.email.data
            pwd = form.password.data

            if email == os.getenv("AUTH_EMAIL") and pwd == os.getenv("AUTH_PWD"):
                user = User()
                user.id = email
                flask_login.login_user(user, remember=True, duration=datetime.timedelta(minutes=15))
            else:
                flask.flash("login failed", "warning")

        return render_template("testpage.html",form=form)
    return app

