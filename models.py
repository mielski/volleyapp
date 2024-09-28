"""Domain models for the trainings app"""
import uuid
from datetime import date, datetime
from typing import Optional, List

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
    attendees: Optional[PositiveInt] = Field(default=None, description="Number of players that attend the training")



if __name__ == '__main__':

    tm1 = TrainingModel(title="Dribbelen voor Dummies", date=date.today())
    print(tm1)
    print(tm1.model_dump(by_alias=True))