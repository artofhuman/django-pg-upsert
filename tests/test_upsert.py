import pytest
from .starwars import models

from django_pg_upsert import insert_conflict, InsertSql


class TestSqlExpression:
    def test_without_pass_params(self):
        pet = models.Pet(age=12)

        sql = InsertSql(pet).to_sql()

        assert (
            sql
            == "INSERT INTO starwars_pet (name, age) VALUES ('', '12') ON CONFLICT  DO NOTHING RETURNING *"
        )


@pytest.mark.django_db
def test_upsert_without_arguments():
    pet = models.Pet(age=12)

    insert_conflict(pet)
    insert_conflict(pet)

    records = models.Pet.objects.all()

    assert len(records) == 1
    record = records[0]
    assert record.age == 12
    assert record.name == ''
