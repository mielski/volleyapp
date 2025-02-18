import pytest
from pydantic import ValidationError

import app.models as models
from models import DifficultyLevel


class TestExerciseLink:

    @pytest.fixture(autouse=True)
    def examples(self):

        self.by_ref = models.ExerciseLink(ref_id="3")
        self.by_model = models.ExerciseLink(model={"title": "hello there", "difficulty_level": "Beginner"})

    def test_model_vanilla(self):

        ex_link = models.ExerciseLink(ref_id="3")

        assert self.by_ref.ref_id == "3"
        assert self.by_ref.model is None


    def test_model_data_proper(self):

        assert self.by_model.model.title == "hello there"
        assert self.by_model.model.approach == ""
        assert self.by_model.model.difficulty_level == DifficultyLevel.beginner
        assert self.by_model.ref_id is None

    def test_model_requires_1_argument(self):
        """tests post validation that requires either the ref_id or the model to be defined."""

        with pytest.raises(AttributeError):
            models.ExerciseLink()

        with pytest.raises(AttributeError):
            models.ExerciseLink(ref_id="a", model={"title": "hello", "difficulty_level": "Beginner"})
