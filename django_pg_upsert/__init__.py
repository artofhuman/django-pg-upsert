__version__ = "0.6.1"


import django.db
from django.db import connections
from django.db.models.sql import Query
from django.db.models.sql.compiler import SQLInsertCompiler

try:
    # Django >= 4.1
    from django.db.models.constants import OnConflict
except ImportError:
    OnConflict = None


def listify(var):
    if isinstance(var, list):
        return var
    else:
        return [var]


class IgnoreConflictSuffix:
    _SQL = "ON CONFLICT {conflict_sql} {action_sql}"
    _DO_NOTHING = "DO NOTHING"

    def __init__(self, constraint=None, fields=None, update=None, update_where=None):
        self._constraint = constraint
        self._fields = fields
        self._update = update
        self._update_where = update_where

        if self._constraint and self._fields:
            raise ValueError("Only fields or constraint args can be used")

        if self._update_where is not None and not self._update:
            raise ValueError("update_where arg can be used only with update arg")

    def as_sql(self, model, connection):
        where_sql, where_params = self._where_sql(model, connection)

        sql = self._SQL.format(
            conflict_sql=self._conflict_sql(connection),
            action_sql=self._action_sql(connection),
        )

        if where_sql:
            sql = f"{sql} WHERE {where_sql}"

        return sql, where_params

    def has_conflict_target(self):
        return bool(self._constraint) or bool(self._fields)

    def _conflict_sql(self, connection) -> str:
        if self._constraint:
            return "ON CONSTRAINT " + self._constraint

        if self._fields:
            fields = ", ".join([connection.ops.quote_name(f) for f in self._fields])
            return "(%s)" % fields

        return ""

    def _action_sql(self, connection) -> str:
        if self._update:
            fields = ", ".join(
                [f"{connection.ops.quote_name(f)} = EXCLUDED.{connection.ops.quote_name(f)}" for f in self._update]
            )
            return f"DO UPDATE SET {fields}"
        return self._DO_NOTHING

    def _where_sql(self, model, connection):
        if self._update_where is None:
            return "", ()

        # Raw sql condition is used as is, e.g. "EXCLUDED.age > starwars_pet.age"
        if isinstance(self._update_where, str):
            return self._update_where, ()

        query = Query(model)
        where = query.build_where(self._update_where)
        compiler = query.get_compiler(connection=connection)
        return where.as_sql(compiler, connection)


class SQLUpsertCompiler(SQLInsertCompiler):
    _REWRITE_PART = "ON CONFLICT DO NOTHING"

    ignore_conflicts_suffix = None

    def as_sql(self):
        sql = super().as_sql()

        if self.ignore_conflicts_suffix.has_conflict_target():
            conflict_part, conflict_params = self.ignore_conflicts_suffix.as_sql(self.query.model, self.connection)

            return [
                (
                    self._rewrite_sql_statement(query, conflict_part),
                    self._merge_params(params, conflict_params),
                )
                for query, params in sql
            ]
        else:
            return sql

    @staticmethod
    def _merge_params(params, conflict_params):
        if not conflict_params:
            return params
        return tuple(params) + tuple(conflict_params)

    def _rewrite_sql_statement(self, query: str, new_conflict_part):
        return query.replace(self._REWRITE_PART, new_conflict_part)


class UpsertQuery(django.db.models.sql.InsertQuery):
    def get_compiler(self, using=None, connection=None):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]
        return SQLUpsertCompiler(self, connection, using)


class Upsert:
    def __init__(
        self,
        obj,
        db=None,
        constraint=None,
        fields=None,
        update=None,
        update_where=None,
    ):
        self._obj = listify(obj)
        self._db = db
        self._ignore_conflicts = IgnoreConflictSuffix(constraint, fields, update, update_where)

        if self._db is None:
            self._db = self._model._default_manager.db

    def as_sql(self):
        return self._get_compiler().as_sql()

    def execute(self):
        return self._get_compiler().execute_sql()

    def _get_compiler(self):
        fields = [f for f in self._meta.concrete_fields if not f.auto_created]

        query = UpsertQuery(self._model, **self._ignore_conflicts_kwargs())
        query.insert_values(fields, self._obj, raw=False)

        compiler: SQLUpsertCompiler = query.get_compiler(self._db)
        compiler.ignore_conflicts_suffix = self._ignore_conflicts
        return compiler

    @staticmethod
    def _ignore_conflicts_kwargs():
        if OnConflict is None:
            return {"ignore_conflicts": True}
        return {"on_conflict": OnConflict.IGNORE}

    @property
    def _meta(self):
        return self._obj[0]._meta

    @property
    def _model(self):
        return self._meta.model


class PgUpsertManager(django.db.models.Manager):
    def insert_conflict(self, data, constraint=None, fields=None, update=None, update_where=None):
        data = listify(data)
        objects = [self.model(**model_data) for model_data in data]
        return Upsert(objects, self.db, constraint, fields, update, update_where).execute()


def insert_conflict(obj, constraint=None, fields=None, update=None, update_where=None):
    obj = listify(obj)
    db = obj[0]._meta.default_manager.db
    return Upsert(obj, db, constraint, fields, update, update_where).execute()
