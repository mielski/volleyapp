import base64
import os
from logging import basicConfig, INFO, getLogger
from pathlib import Path

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
from storage import BlobStorageUrlBuilder

CONTAINERNAME = "volleyimages"

basicConfig(level=INFO)

logger = getLogger(__name__)
class LocalStorageClient:

    def __init__(self, storage_dir: str | Path):
        """

        :param storage_dir: path towards which to store the data
        """

        self.storage_dir = Path(storage_dir).absolute()
        if not os.path.exists(self.storage_dir):
            os.mkdir(self.storage_dir)

    def upload_blob(self, filename, data):

        path = self.storage_dir / filename
        with open(path, "wb") as fid:
            fid.write(data)
        logger.info(f"file written to {path}")

    def download_blob(self, filename):

        return open(self.storage_dir / filename, "rb")


def b64encode(data):
    return base64.b64encode(data).decode('utf-8')



def create_app():
    """create the volleybal exercise application."""
    app = MyTrainingsApp(__name__)
    app.secret_key = 'dev'

    load_dotenv(".")
    app.db = MongoClient(os.environ["MONGO_URI"])['trainings_database']
    app.db.trainings = app.db['trainings']
    app.db.exercises = app.db['exercises']
    app.filelist = {} # temporary

    if os.getenv("STORAGE_CONNECTION_STRING") and not os.getenv("LOCAL_STORAGE") == "TRUE":
        storage_client = BlobServiceClient.from_connection_string(os.getenv("STORAGE_CONNECTION_STRING"))
        app.blob_storage = storage_client.get_container_client(CONTAINERNAME)
        app.blob_url_builder = BlobStorageUrlBuilder(storage_client, CONTAINERNAME)

    else:
        logger.info("no storage account defined -> using local")
        app.blob_storage = LocalStorageClient(Path(__file__).parent / "static/img")


    # Register frontend blueprints
    app.register_blueprint(trainings_bp)
    app.register_blueprint(exercises_bp)

    #register backend blueprints
    app.register_blueprint(exercises_api_bp)
    app.register_blueprint(actions_api_bp)

    bootstrap = Bootstrap5(app)
    app.jinja_env.filters['b64encode'] = b64encode

    @app.route('/')
    def index():  # immediate redirect to view

        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule}")

        return render_template("index.html")

    @app.route("/testpage", methods=["GET", "POST"])
    def testpage():
        """page used during development"""

        _id = app.db.exercises.find_one()["_id"]

        if request.method == "POST":
            print(list(request.form.values()))
            print(list(request.form.items()))
            print(request.data)

            if filelist := request.files.getlist("image_uploads"):
                for file_ in filelist:
                    print(f"got {len(filelist)} files")
                    file_data = file_.read()
                    mime_type = file_.mimetype
                    print(f"storing file to blob storage")
                    app.filelist[file_.filename] = (file_data, mime_type)

        return render_template("testpage.html", exercise_id=_id, filelist=app.filelist)
    return app
