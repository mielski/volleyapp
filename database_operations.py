from pprint import pprint

from dotenv import load_dotenv
from pymongo.synchronous.collection import Collection

from models import TrainingModel, VolleyballExercise, DifficultyLevel, Skills

load_dotenv()
from main import app


# docker run -p 27017:27017 --name mongo_trainings --pull missing mongo:latest

trainings: Collection = app.db.trainings
exercises: Collection = app.db.exercises

def delete_all():
    trainings.delete_many({})
    exercises.delete_many({})


def fetch_all():
    for entry in trainings.find({}):
        print(entry)
    for entry in exercises.find({}):
        pprint(entry)


def add_some_trainings():
    """Adds two trainings to the trainings collection"""

    tm1 = TrainingModel(title="Passing - houding voeten", date="2024-09-20", rating=1,
                        description="Doel: oefenen op het klaarstaan voor de bal met juiste houding voetenwerk.")
    tm2 = TrainingModel(title="Passing - beweging naar bal", date="2024-09-27", rating=1,
                        description="Doel: oefenen op balbaanbehoordeling en achter de bal komen")

    trainings.insert_one(tm1.model_dump(by_alias=True))
    trainings.insert_one(tm2.model_dump(by_alias=True))


def add_some_exercises():

    exercices_to_add = [
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
        exercises.insert_one(VolleyballExercise(**exercise_data).model_dump(by_alias=True))
        exercises.insert_one(VolleyballExercise(**exercise_data).model_dump(by_alias=True))


if __name__ == '__main__':

    delete_all()
    add_some_trainings()
    add_some_exercises()
    fetch_all()
