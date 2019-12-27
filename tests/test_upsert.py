import datetime

import pytest
from freezegun import freeze_time
from django.db.utils import ProgrammingError

import django_pg_upsert
from .starwars import models
from .starwars.models import Pet, Human


@pytest.fixture
def pet():
    return models.Pet(age=12, name="dog")


@freeze_time('2020-01-01 12:00:00')
class TestSqlExpression:
    def test_without_pass_params(self, pet):
        sql = django_pg_upsert.Upsert(pet).as_sql()

        assert sql == [
            (
                'INSERT INTO "starwars_pet" ("name", "alias_name", "age", "created_at", "updated_at", "owner_id") VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING',
                ("dog", None, 12, datetime.datetime(2020, 1, 1, 12, 0), datetime.datetime(2020, 1, 1, 12, 0), None),
            )
        ]

    def test_with_constraint(self, pet):
        sql = django_pg_upsert.Upsert(pet, constraint="starwars_pet_name_key").as_sql()

        assert sql == [
            (
                'INSERT INTO "starwars_pet" ("name", "alias_name", "age", "created_at", "updated_at", "owner_id") VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT ON CONSTRAINT starwars_pet_name_key DO NOTHING',
                ("dog", None, 12, datetime.datetime(2020, 1, 1, 12, 0), datetime.datetime(2020, 1, 1, 12, 0), None),
            )
        ]

    def test_with_fields(self, pet):
        sql = django_pg_upsert.Upsert(pet, fields=['name']).as_sql()

        assert sql == [
            (
                'INSERT INTO "starwars_pet" ("name", "alias_name", "age", "created_at", "updated_at", "owner_id") VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT ("name") DO NOTHING',
                ("dog", None, 12, datetime.datetime(2020, 1, 1, 12, 0), datetime.datetime(2020, 1, 1, 12, 0), None),
            )
        ]


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

    def test_upsert_with_constraint_name(self):
        Pet.objects.insert_conflict(
            data={"name": "dog", "age": 12}, constraint="starwars_pet_name_key"
        )
        res = Pet.objects.insert_conflict(
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

        models.Pet(age=12, name="dog").save()

    def test_with_fk_relations(self):
        owner = Human(name='John')
        owner.save()

        owner.pet_set.insert_conflict(data={"name": "dog", "age": 12})
        owner.pet_set.insert_conflict(data={"name": "dog", "age": 12})

        self.assert_create_single_record()


    def test_upsert_with_field_names(self):
        Pet.objects.insert_conflict(
            data={"name": "dog", "age": 12}, fields=["name"]
        )

        Pet.objects.insert_conflict(
            data={"name": "dog", "age": 20}, fields=["name"]
        )

        self.assert_create_single_record()

    def test_use_constraint_and_fields_in_same_time(self):
        with pytest.raises(ValueError):
            Pet.objects.insert_conflict(
                data={"name": "dog", "age": 20},
                fields=["name"],
                constraint='starwars_pet_name_key'
            )

    def test_standalone_method(self, pet):
        django_pg_upsert.insert_conflict(pet)
        django_pg_upsert.insert_conflict(pet)

        self.assert_create_single_record()

    def test_standalone_method_with_constraint(self, pet):
        django_pg_upsert.insert_conflict(pet, constraint='starwars_pet_name_key')
        django_pg_upsert.insert_conflict(pet, constraint='starwars_pet_name_key')

        self.assert_create_single_record()

    def test_standalone_method_with_fields(self, pet):
        django_pg_upsert.insert_conflict(pet, fields=['name'])
        django_pg_upsert.insert_conflict(pet, fields=['name'])

        self.assert_create_single_record()
