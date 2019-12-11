__version__ = "0.1.0"


import django.db
from django.db import connection
from django.db import models, router
from django.db.models.sql import InsertQuery
from django.db.models.sql.compiler import SQLInsertCompiler


# class SQLUpsertCompiler:#(django.db.models.sql.compiler.SQLInsertCompiler):
    # pass


class UpsertQuery(django.db.models.sql.InsertQuery):
    pass


class Upsert:
    def __init__(self, obj, db=None):
        self._obj = obj
        self._db = db

        if self._db is None:
            self._db = self._model._default_manager.db

    def as_sql(self):
        return self._get_compiled_query().as_sql()

    def execute(self):
        return self._get_compiled_query().execute_sql()

    def _get_compiled_query(self):
        fields = [f for f in self._meta.concrete_fields if not f.auto_created]

        query = UpsertQuery(self._model, ignore_conflicts=True)
        query.insert_values(fields, [self._obj], raw=True)

        return query.get_compiler(self._db)

    @property
    def _meta(self):
        return self._obj._meta

    @property
    def _model(self):
        return self._meta.model


class Manager(django.db.models.Manager):
    def insert_conflict(self, data, constraint=None):
        obj = self.model(**data)

        return Upsert(obj, self.db).execute()
