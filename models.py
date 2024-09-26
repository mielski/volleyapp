"""Domain models for the trainings app"""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class TrainingModel(BaseModel):
    """Model for the data about a training"""
    id_: bytes = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    training_date: date = Field(alias="date", title="Date of the training")
    creation_date: datetime = Field(default_factory=lambda: datetime.utcnow(),
                                    title="Datestamp when the training was created.")



if __name__ == '__main__':

    tm1 = TrainingModel(title="Dribbelen voor Dummies", date=date.today())
    print(tm1)