import datetime

import pytest
from freezegun import freeze_time
from django.db.utils import ProgrammingError

from .starwars import models
from .starwars.models import Pet
from django_pg_upsert import Upsert

# TODO: test auto filled fields created_at
# TODO: check with associations


@pytest.fixture
def pet():
    return models.Pet(age=12, name="dog")


@freeze_time('2020-01-01 12:00:00')
class TestSqlExpression:
    def test_without_pass_params(self, pet):
        sql = Upsert(pet).as_sql()

        assert sql == [
            (
                'INSERT INTO "starwars_pet" ("name", "alias_name", "age", "created_at", "updated_at") VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING',
                ("dog", None, 12, datetime.datetime(2020, 1, 1, 12, 0), datetime.datetime(2020, 1, 1, 12, 0)),
            )
        ]

    def test_with_constraint(self, pet):
        sql = Upsert(pet, constraint="starwars_pet_name_key").as_sql()

        assert sql == [
            (
                'INSERT INTO "starwars_pet" ("name", "alias_name", "age", "created_at", "updated_at") VALUES (%s, %s, %s, %s, %s) ON CONFLICT ON CONSTRAINT starwars_pet_name_key DO NOTHING',
                ("dog", None, 12, datetime.datetime(2020, 1, 1, 12, 0), datetime.datetime(2020, 1, 1, 12, 0)),
            )
        ]

    # def test_with_fields(self, pet):
    # sql = UpsertSql(pet, fields=["name"]).to_sql()

    # assert (
    # sql
    # == "INSERT INTO starwars_pet (name, age) VALUES ('dog', '12') ON CONFLICT (name) DO NOTHING RETURNING *"
    # )


@pytest.mark.django_db
class TestInsertConflict:
    def assert_create_single_record(self):
        records = models.Pet.objects.all()

        assert len(records) == 1
        record = records[0]
        assert record.age == 12
        assert record.name == "dog"

    def test_upsert_without_arguments(self):
        Pet.objects.insert_conflict(data={"name": "dog", "age": 12})
        Pet.objects.insert_conflict(data={"name": "dog", "age": 20})

        self.assert_create_single_record()

    def test_upsert_with_constraint_name(self, pet):
        Pet.objects.insert_conflict(
            data={"name": "dog", "age": 12}, constraint="starwars_pet_name_key"
        )
        Pet.objects.insert_conflict(
            data={"name": "dog", "age": 20}, constraint="starwars_pet_name_key"
        )

        self.assert_create_single_record()

        with pytest.raises(ProgrammingError):
            Pet.objects.insert_conflict(
                data={"name": "dog", "age": 20}, constraint="unknown"
            )

    def test_not_raise_error(self, pet):
        Pet.objects.insert_conflict(
            data={"name": "yoda", "age": 12}, constraint="starwars_pet_name_key"
        )

        pet.save()

    # def test_upsert_with_field_names(self, pet):
    # insert_conflict(pet, fields=["name"])
    # insert_conflict(pet, fields=["name"])

    # self.assert_create_single_record()

    # def test_pass_field_without_uniq(self, pet):
    # with pytest.raises(ProgrammingError):
    # insert_conflict(pet, fields=["age", "name"])

    # def test_pass_unknown_field(self, pet):
    # with pytest.raises(ProgrammingError):
    # insert_conflict(pet, fields=["unknown"])

    # def test_pass_constraint_and_fields_together(self, pet):
    # with pytest.raises(RuntimeError):
    # insert_conflict(pet, fields=["name"], constraint="starwars_pet_name_key")
