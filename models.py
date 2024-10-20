"""Domain models for the trainings app"""
import uuid
from datetime import date, datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, Field, conint, PositiveInt


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


class ExerciseModel(BaseModel):
    """Model for the data about an exercise."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, alias="_id")
    title: str = Field(max_length=100, title="Title of the exercise")
    duration: int = None
    approach: str = Field(default="", title="Approach of how the exercise is conducted")


    # for later development
    image_uris: List[str] = Field(default_factory=lambda: dict(),
                                  description="list of image uris",
                                  examples=[["https://blobstorage/trainings/image1.png",
                                             "https://blobstorage/trainings/image2.png"]])


if __name__ == '__main__':

    tm1 = TrainingModel(title="Dribbelen voor Dummies", date=date.today(), notes="hey, gaat dit goed?")
    print(tm1)
    print(tm1.model_dump(by_alias=True))

    ex1 = ExerciseModel(title="Service 2 4 5 7 9",
                        duration=5,
                        approach="""
1 ball per 2 players. 1) Player 1 serves the ball at 2 meters from the net towards 
the second player, which stands at the 7 meter on the other side of the net. The 
second player catches the ball and rolls is back to player 1. This repeats five times 
and then the players switch position. 
After success, repeat with 4 meters, etc.""")

    print(ex1)