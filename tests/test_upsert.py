import pytest
from .starwars import models


@pytest.mark.django_db
def test_upsert():
    pet = models.Pet(age=12)
    pet.save()
    pass
