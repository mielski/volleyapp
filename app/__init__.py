import os

from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient
from dotenv import load_dotenv
from flask import redirect, url_for, jsonify, render_template, request
from flask_bootstrap import Bootstrap5
from pymongo import MongoClient

from app.blueprints.frontends.trainings import trainings_bp
from app.blueprints.frontends.exercises import exercises_bp
from app.training_app import MyTrainingsApp
from blueprints.backends.exercises_api import exercises_api_bp
from blueprints.backends.actions_api import actions_api_bp


def create_app():
    """create the volleybal exercise application."""
    app = MyTrainingsApp(__name__)
    app.secret_key = 'dev'

    load_dotenv(".")
    app.db = MongoClient(os.environ["MONGO_URI"])['trainings_database']
    app.db.trainings = app.db['trainings']
    app.db.exercises = app.db['exercises']

    if os.getenv("STORAGE_CONNECTION_STRING"):
        storage_client = BlobServiceClient.from_connection_string(os.getenv("STORAGE_CONNECTION_STRING"))
        app.blob_storage = storage_client.get_container_client("volleyimages")
    else:
        print("no storage account defined")
        app.storage = None

        ContainerClient

    # Register frontend blueprints
    app.register_blueprint(trainings_bp)
    app.register_blueprint(exercises_bp)

    #register backend blueprints
    app.register_blueprint(exercises_api_bp)
    app.register_blueprint(actions_api_bp)

    bootstrap = Bootstrap5(app)

    @app.route('/')
    def index():  # immediate redirect to view

        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule}")

        return render_template("index.html")

    @app.route("/testpage", methods=["GET", "POST"])
    def testpage():
        """page used during development"""

        if request.method == "POST":
            print(list(request.form.values()))
            print(list(request.form.items()))
            print(request.data)

            if file := request.files["image_uploads"]:
                print(f"trying to read the file {file.filename}")
                file_data = file.read()

                print(f"storing file to blob storage")
                app.blob_storage.upload_blob(file.filename, file_data)

        return render_template("testpage.html")
    return app
