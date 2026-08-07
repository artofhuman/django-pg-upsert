# django-pg-upsert

![build](https://github.com/artofhuman/django-pg-upsert/workflows/build/badge.svg)
[![PyPI version](https://badge.fury.io/py/django-pg-upsert.svg)](https://badge.fury.io/py/django-pg-upsert)
[![Downloads](https://img.shields.io/pypi/dm/django-pg-upsert)](https://img.shields.io/pypi/dm/django-pg-upsert)


This package adds support for the native Postgres upsert (INSERT ... ON CONFLICT) to Django.

# Installation

`pip install django-pg-upsert`

# Usage

## As a manager
```python
from django.db import models

from django_pg_upsert import PgUpsertManager


class Pet(models.Model):
    name = models.CharField(max_length=30, unique=True)
    age = models.PositiveIntegerField()

    objects = PgUpsertManager()


Pet.objects.insert_conflict(data={"name": "dog", "age": 12})

# The second query does not insert a record and does not raise an error.
Pet.objects.insert_conflict(data={"name": "dog", "age": 20})
```

This code produces the SQL statement:

```python
[
  'INSERT INTO "pets" ("name", "age") VALUES (%s, %s) ON CONFLICT DO NOTHING',
  ("dog", 12),
]
```

### Explicit constraint name

``` python
Pet.objects.insert_conflict(
  data={"name": "dog", "age": 12},
  constraint="pet_name_uniq"
)

[
  'INSERT INTO "pets" ("name", "age") VALUES (%s, %s) ON CONFLICT ON CONSTRAINT pet_name_uniq DO NOTHING',
  ("dog", 12),
]

```

### Using field names


``` python
Pet.objects.insert_conflict(
  data={"name": "dog", "age": 12},
  fields=["name"]
)

[
  'INSERT INTO "pets" ("name", "age") VALUES (%s, %s) ON CONFLICT ("name") DO NOTHING',
  ("dog", 12),
]

```

## As a standalone function

```python
import django_pg_upsert

pet = Pet(name="dog", age=12)

django_pg_upsert.insert_conflict(pet)
django_pg_upsert.insert_conflict(pet, constraint="pet_name_uniq")
django_pg_upsert.insert_conflict(pet, fields=["name"])
```

## Update

``` python
Pet.objects.insert_conflict(
  data={"name": "dog", "age": 100},
  fields=["name"],
  update=["age"]
)
```
or

```python
django_pg_upsert.insert_conflict(pet, fields=["name"], update=["age"])
```

```python
[
  'INSERT INTO "pets" ("name", "age") VALUES (%s, %s) ON CONFLICT ("name") DO UPDATE SET age = EXCLUDED.age',
  ("dog", 100),
]

```

## Update with condition

The `update_where` argument restricts which existing rows are updated
(`ON CONFLICT ... DO UPDATE SET ... WHERE ...`). It accepts a `Q` object.

``` python
from django.db.models import Q

Pet.objects.insert_conflict(
  data={"name": "dog", "age": 100},
  fields=["name"],
  update=["age"],
  update_where=Q(age__lt=100),
)

[
  'INSERT INTO "pets" ("name", "age") VALUES (%s, %s) ON CONFLICT ("name") DO UPDATE SET age = EXCLUDED.age WHERE "pets"."age" < %s',
  ("dog", 100, 100),
]
```

The argument also accepts a raw SQL string. Use a raw string to reference the
proposed row through `EXCLUDED`.

``` python
django_pg_upsert.insert_conflict(
  pet,
  fields=["name"],
  update=["age"],
  update_where="EXCLUDED.age > pets.age",
)

[
  'INSERT INTO "pets" ("name", "age") VALUES (%s, %s) ON CONFLICT ("name") DO UPDATE SET age = EXCLUDED.age WHERE EXCLUDED.age > pets.age',
  ("dog", 100),
]
```

Do not build a raw string from user input. The package inlines the string into
the statement as is.

## Batch

To insert many rows in one statement, pass a list. The manager accepts a list
of dictionaries. The standalone function accepts a list of model objects. All
other arguments work as they do for a single row.

``` python
Pet.objects.insert_conflict(
  data=[
    {"name": "dog", "age": 12},
    {"name": "cat", "age": 8},
  ],
  fields=["name"],
  update=["age"],
)
```
or

```python
dog = Pet(name="dog", age=12)
cat = Pet(name="cat", age=8)

django_pg_upsert.insert_conflict([dog, cat], fields=["name"], update=["age"])
```

Both calls produce one statement with one row set for each object:

```python
[
  'INSERT INTO "pets" ("name", "age") VALUES (%s, %s), (%s, %s) ON CONFLICT ("name") DO UPDATE SET age = EXCLUDED.age',
  ("dog", 12, "cat", 8),
]
```

# Motivation

[django-postgres-extra](https://github.com/SectorLabs/django-postgres-extra) also
has a pg upsert method, but that package requires a different DB backend in the
Django settings. Sometimes this change is not possible.

django-pg-upsert solves only one problem and depends only on Django. It is not a
Swiss army knife.
