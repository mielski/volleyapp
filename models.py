"""Domain models for the trainings app"""
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict

from pydantic import BaseModel, Field, conint, PositiveInt, HttpUrl


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


# Define the VolleyballExercise model
class VolleyballExercise(BaseModel):
    """Defines the VolleybalExercise model"""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex, alias="_id")
    name: str
    description: str
    approach: str = Field(default="", title="Approach of how the exercise is conducted")
    difficulty_level: DifficultyLevel
    duration: conint(ge=0)  # Duration in seconds, must be non-negative
    reps: Optional[conint(ge=0)] = Field(default=None)  # Optional
    sets: Optional[conint(ge=0)] = Field(default=None)  # Optional
    skill_focus: List[str]  # List of skills
    equipment: Optional[List[str]] = Field(default=None)  # List of equipment
    video_url: Optional[HttpUrl] = Field(default=None)  # Optional, must be a valid URL
    image_uris: List[HttpUrl] = Field(default_factory=lambda: dict(),
                                  description="list of image uris",
                                  examples=["https://blobstorage/trainings/image1.png",
                                             "https://blobstorage/trainings/image2.png"])  # Optional, must be a valid URL
    target_heart_rate: Optional[int] = Field(default=None)  # Optional
    created_at: datetime = Field(default_factory=lambda: datetime.now())  # Automatically set to now
    updated_at: datetime = Field(default_factory=lambda: datetime.now())  # Automatically set to now
    tags: List[str] = Field(default_factory=lambda: list())  # Default to an empty list
    exercise_variant: Optional[str] = Field(default=None)  # Optional
    related_exercises: Optional[List[str]] = Field(default_factory=lambda: list())  # List of related exercise IDs

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Spiking Drill",
                "description": "A drill to improve spiking technique.",
                "approach": "1) Trainer passes ball to Lib.\n2) Lib pass to Set\n3)Set to spiker.\n4) attack",
                "difficulty_level": "Intermediate",
                "duration": 300,
                "reps": 10,
                "sets": 3,
                "skill_focus": ["spiking"],
                "equipment": ["Volleyball"],
                "calories_burned": 150,
                "video_url": "https://example.com/video",
                "image_uris": ["https://example.com/image"],
                "created_by": "coach123",
                "tags": ["volleyball", "drill", "spiking"],
                "exercise_variant": "Jump Spike",
                "related_exercises": ["exercise_id_1", "exercise_id_2"]
            }
        }


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