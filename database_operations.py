import os
from pprint import pprint

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection

from app.models import TrainingModel, ExerciseModel, DifficultyLevel, Skills

load_dotenv()


db = MongoClient(os.environ["MONGO_URI"])['trainings_database']
# docker run -p 27017:27017 --name mongo_trainings --pull missing mongo:latest
CONTAINER_URI = os.getenv("STORAGE_CONTAINER_URI")

trainings: Collection = db.trainings
exercises: Collection = db.exercises

def delete_all():
    trainings.delete_many({})
    exercises.delete_many({})


def fetch_all():
    """pretty print the data in the database"""
    print("Trainings")
    for entry in trainings.find({}):
        pprint(entry)
    print("")
    print("Exercises")
    for entry in exercises.find({}):
        pprint(entry)


def add_some_trainings():
    """Adds two trainings to the trainings collection"""

    tm1 = TrainingModel(_id="test_training1",
                        title="Passing - houding voeten", date="2024-12-16", rating=1,
                        description="Doel: oefenen op het klaarstaan voor de bal met juiste houding voetenwerk.")
    tm2 = TrainingModel(_id="testt_training2",
                        title="Passing - beweging naar bal", date="2024-12-09", rating=1,
                        description="Doel: oefenen op balbaanbehoordeling en achter de bal komen",
                        )

    trainings.insert_one(tm1.model_dump(by_alias=True))
    trainings.insert_one(tm2.model_dump(by_alias=True))


def add_some_exercises():

    exercices_to_add = [
        dict(
            title="Circuit 5 ballen",
            approach="spelers doen een circuit van 5 balacties. <ul><li>Blok op buiten</li><li>"
            "Aflopen en geslagen bal verdedigen van over net</li><li>Diepe bal positie 6</li></ul>",
            difficulty_level=DifficultyLevel.advanced,
            skill_focus=[Skills.Footwork, Skills.Defense],
            duration=10,
            intensity=3,
            image_urls=[CONTAINER_URI + "tactical-board.com (10).png",
                        CONTAINER_URI + "tactical-board.com (9).png"]
            ),
        dict(
            title="Vlinder - single Passer",
            approach="Controlled serve to <i>passer</i>, passer to catcher at SV position. catcher indicates quality of pass",
            rotation="Players move to next position after 10 successful serves",
            difficulty_level=DifficultyLevel.beginner,
            skill_focus=[Skills.Serving, Skills.Defense],
            duration=10,
            intensity=3,
            ),
        dict(
            title="Pepper with fixed setter",
            approach="Two attackers 5 meter and Setter. Play ball to setter, setter returns the ball and then "
                     "player A spikes to player B. B passes to Setter and back for spike of B to A, etc. "
                     "Optionally, setter can also switch position.",
            intensity=4,
            rotation="Not required, play for fixed time. Possibly rotate setters.",
            difficulty_level=DifficultyLevel.advanced,
            duration=10,
            skill_focus=[Skills.Defense, Skills.Attacking, Skills.Footwork],
            video_url="https://www.youtube.com/watch?v=-ZZuo-Yev9E"
        ),
        dict(title="Inslaan met afstemming",
             approach="Doel van deze oefening is dat aanvallers makkelijk tussendoor met de SV\n "
                      "kunnen terugkoppelen, terwijl de oefening met nieuwe aanvallers doorloopt. <br>"
                      "rijtje met buiten aanvallers en rijtje met middens / Dias. <br>"
                      "1. Aangooi op SV<br>"
                      "2. SV speelt op buiten of midden/achterover.<br>"
                      "- herhaal zodat beide spelers 3 ballen hebben gekregen",
             duration=10,
             skill_focus=[Skills.Attacking],
             difficulty_level=DifficultyLevel.advanced,
             )
    ]
    for exercise_data in exercices_to_add:
        exercises.insert_one(ExerciseModel(**exercise_data).model_dump(by_alias=True))


def add_exercises_to_first_training():
    """add exercise 0 and 2 to the first training"""
    training_id = trainings.find_one()["_id"]
    exercises_ids = [v["_id"] for v in exercises.find({}, {"_id": 1})]
    ids_to_add = exercises_ids[0], exercises_ids[2]
    trainings.update_one({"_id": training_id}, {"$push": {"exercises": {"$each": ids_to_add}}})

if __name__ == '__main__':

    delete_all()
    add_some_trainings()
    add_some_exercises()
    # link exercises to the first training

    add_exercises_to_first_training()

    fetch_all()
