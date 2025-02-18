import pytest
from pydantic import ValidationError

import app.models as models
from models import DifficultyLevel


class TestExerciseLink:

    def test_model_vanilla(self):

        ex_link = models.ExerciseLink(ref_id="3")

        assert ex_link.ref_id == "3"
        assert ex_link.model is None


    def test_model_data_proper(self):

        ex = models.ExerciseLink(model={"title": "hello there", "difficulty_level": "Beginner"})

        assert ex.model.title == "hello there"
        assert ex.model.approach == ""
        assert ex.model.difficulty_level == DifficultyLevel.beginner

    def test_model_requires_1_argument(self):
        """tests post validation that requires either the ref_id or the model to be defined."""

        with pytest.raises(AttributeError):
            models.ExerciseLink()

        with pytest.raises(AttributeError):
            models.ExerciseLink(ref_id="a", model={"title": "hello", "difficulty_level": "Beginner"})
