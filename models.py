"""Domain models for the trainings app"""
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict

from pydantic import BaseModel, Field, conint, PositiveInt, HttpUrl, field_serializer
from pydantic_core import Url


class TrainingModel(BaseModel):
    """Model for the data about a training"""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, alias="_id")
    title: str
    description: str = ""
    training_date: datetime = Field(alias="date", title="Date of the training")
    creation_date: datetime = Field(default_factory=lambda: datetime.now(),
                                    title="Datestamp when the training was created.")
    rating: conint(ge=0, le=5) = Field(default=None,
                                       description="The rating of the training between 0 and 5 (optional)")
    tags: List[str] = Field(default_factory=lambda: list(),
                            description="Tags to identify patterns in the training, for example 'defence'"
                            )
    notes: str = Field(default="", description="Notes/comments made during / after the training")
    attendees: Optional[PositiveInt] = Field(default=None, description="Number of players that attends the training")


# Enum for difficulty levels
class DifficultyLevel(str, Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"


# Enum for exercise categories
class ExerciseCategory(str, Enum):
    skill = "Skill"
    conditioning = "Conditioning"
    tactics = "Tactics"


class Skills(str, Enum):
    Serving = "Serving"
    ServicePass = "ServicePass"
    Attacking = "Attacking"
    Blocking = "Blocking"
    Defense = "Defense"
    Footwork = "Footwork"



# Define the VolleyballExercise model
class VolleyballExercise(BaseModel):
    """Defines the VolleybalExercise model"""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex, alias="_id")
    title: str
    approach: str = Field(default="", title="Approach of how the exercise is conducted", examples=[
        ["player 1 passes to 2, 2 sets to 3, 3 spikes the ball over the net"]])
    difficulty_level: DifficultyLevel
    duration: conint(ge=0)  # Duration in seconds, must be non-negative
    skill_focus: List[Skills] = Field(default_factory=lambda: list, title="List of volleybal skills that is included",
                                      )  # List of skills
    intensity: Optional[int] = Field(default=None, title="Intensity of the training (1=low, 5=high)")
    video_url: Optional[HttpUrl] = Field(default=None)  # Optional, must be a valid URL
    image_uris: List[HttpUrl] = Field(default_factory=lambda: list(),
                                      description="list of image uris",
                                      examples=["https://blobstorage/trainings/image1.png",
                                                "https://blobstorage/trainings/image2.png"])  # Optional, must be a valid URL
    created_at: datetime = Field(default_factory=lambda: datetime.now())  # Automatically set to now
    updated_at: datetime = Field(default_factory=lambda: datetime.now())  # Automatically set to now
    tags: List[str] = Field(default_factory=lambda: list())  # Default to an empty list
    related_exercises: Optional[List[str]] = Field(default_factory=lambda: list())  # List of related exercise IDs


    @field_serializer("video_url")
    def serialize_url(self, value: Optional[Url]) -> Optional[str]:
        return str(value) if value else None

    def new(cls):
        """create a new, empty training that meets the minimum requirements"""


if __name__ == '__main__':
    tm1 = TrainingModel(title="Dribbelen voor Dummies", date=date.today(), notes="hey, gaat dit goed?")
    print(tm1)
    print(tm1.model_dump(by_alias=True))

    ex1 = VolleyballExercise(title="Service 2 4 5 7 9",
                             duration=5,
                             approach="""
1 ball per 2 players. 1) Player 1 serves the ball at 2 meters from the net towards 
the second player, which stands at the 7 meter on the other side of the net. The 
second player catches the ball and rolls is back to player 1. This repeats five times 
and then the players switch position. 
After success, repeat with 4 meters, etc.""")

    print(ex1)
