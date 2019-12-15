__version__ = "0.1.0"


import django.db
from django.db import connection, connections
from django.db import models, router
from django.db.models.sql import InsertQuery
from django.db.models.sql.compiler import SQLInsertCompiler


class IgnoreConflictSuffix:
    _SQL = "ON CONFLICT {conflict_sql} DO NOTHING"

    def __init__(self, constraint=None):
        self._constraint = constraint

    def as_sql(self):
        return self._SQL.format(conflict_sql=self._conflict_sql)

    @property
    def _conflict_sql(self) -> str:
        if self._constraint:
            return "ON CONSTRAINT " + self._constraint

        return ''


class SQLUpsertCompiler(django.db.models.sql.compiler.SQLInsertCompiler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.connection.ops.ignore_conflicts_suffix_sql = self.ignore_conflicts_suffix_sql

    def ignore_conflicts_suffix_sql(self, ignore_conflicts: IgnoreConflictSuffix):
        return ignore_conflicts.as_sql()


class UpsertQuery(django.db.models.sql.InsertQuery):
    def get_compiler(self, using=None, connection=None):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]
        return SQLUpsertCompiler(self, connection, using)


class Upsert:
    def __init__(self, obj, db=None, constraint=None):
        self._obj = obj
        self._db = db
        self.constraint = constraint

        if self._db is None:
            self._db = self._model._default_manager.db

    def as_sql(self):
        sql = self._get_compiled_query().as_sql()
        return sql

    def execute(self):
        return self._get_compiled_query().execute_sql()

    def _get_compiled_query(self):
        fields = [f for f in self._meta.concrete_fields if not f.auto_created]

        ignore_conflicts = IgnoreConflictSuffix(self.constraint)

        query = UpsertQuery(self._model, ignore_conflicts=ignore_conflicts)
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

        return Upsert(obj, self.db, constraint).execute()
