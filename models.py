"""Domain models for the trainings app"""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class TrainingModel(BaseModel):
    """Model for the data about a training"""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, alias="_id")
    title: str
    training_date: datetime = Field(alias="date", title="Date of the training")
    creation_date: datetime = Field(default_factory=lambda: datetime.utcnow(),
                                    title="Datestamp when the training was created.")



if __name__ == '__main__':

    tm1 = TrainingModel(title="Dribbelen voor Dummies", date=date.today())
    print(tm1)
    print(tm1.model_dump(by_alias=True))