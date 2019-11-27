__version__ = "0.1.0"


from django.db import connection


SQL = (
    "INSERT INTO {table_name} ({field_names_sql})"
    " VALUES ({values_sql})"
    " ON CONFLICT {conflict_sql} {on_conflict} {return_sql}"
)


def _quote(value):
    return f"'{value}'"


def _get_field_value(entry, field):
    value = getattr(entry, field.attname)
    return _quote(field.get_db_prep_save(value, connection))


class InsertSql:
    def __init__(self, entry):
        self._entry = entry
        self._model = entry.__class__

    def to_sql(self):
        insert_data = self._get_insert_data()
        field_names_sql = ", ".join(insert_data.keys())
        values_sql = ", ".join(insert_data.values())

        sql = SQL.format(
            table_name=self._db_table_name,
            field_names_sql=field_names_sql,
            values_sql=values_sql,
            conflict_sql="",
            on_conflict="DO NOTHING",
            return_sql="RETURNING *",
            # unique_field_names_sql="ON CONSTRAINT " + constraint
        )

        return sql

    @property
    def _db_table_name(self):
        return self._model._meta.db_table

    def _get_insert_data(self):
        insert_data = {}

        fields = self._model._meta.fields

        for field in fields:
            if not field.auto_created:
                insert_data[field.attname] = _get_field_value(self._entry, field)
        return insert_data


def insert_conflict(entry, constraint=None):
    insert = InsertSql(entry)

    with connection.cursor() as cursor:
        cursor.execute(insert.to_sql())
