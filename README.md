# django-pg-upsert

![build](https://github.com/artofhuman/django-pg-upsert/workflows/build/badge.svg)
[![PyPI version](https://badge.fury.io/py/django-pg-upsert.svg)](https://badge.fury.io/py/django-pg-upsert)
[![Downloads](https://img.shields.io/pypi/dm/django-pg-upsert)](https://img.shields.io/pypi/dm/django-pg-upsert)


Support Postgres native upsert (INSERT ... ON CONFLICT) for django

# Installation

`pip install django-pg-upsert`

# Usage

## As a manager
```python

import django_pg_upsert

from django.db import models

class Pet(models.Model):
    name = models.CharField(max_length=30, unique=True)
    age = models.PositiveIntegerField()

    objects = PgUpsertManager()


Pet.objects.insert_conflict(data={"name": "dog", "age": 12})

# second query don't insert record to db and don't raise error
Pet.objects.insert_conflict(data={"name": "dog", "age": 20})

# This code produce SQL statement

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
  'INSERT INTO "pets" ("name", "age") VALUES (%s, %s) ON CONSTRAINT pet_name_uniq DO NOTHING',
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
  'INSERT INTO "pets" ("name", "age") VALUES (%s, %s) ON CONSTRAINT ("name") DO NOTHING',
  ("dog", 12),
]

```

## As a standalone function

```python
import django_pg_upsert

pet = Pet(name='dog', age='12')

django_pg_upsert.insert_conflict(pet)
django_pg_upsert.insert_conflict(pet, constraint='pet_name_uniq')
django_pg_upsert.insert_conflict(pet, fields='name')
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
django_pg_upsert.insert_conflict(pet, fields='name', update=["age"])
```

```python
[
  'INSERT INTO "pets" ("name", "age") VALUES (%s, %s) ON CONFLICT ("name") DO UPDATE SET age = EXCLUDED.age',
  ("dog", 100),
]

```

## Update with condition

The `update_where` argument restricts which existing rows are updated
(`ON CONFLICT ... DO UPDATE SET ... WHERE ...`). It accepts a `Q` object

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

or a raw sql string, which is useful to reference the proposed row via `EXCLUDED`

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

A raw string is inlined into the statement as is, so never build it from
user input.

# Motivation

[django-postgres-extra](https://github.com/SectorLabs/django-postgres-extra) has
a pg upsert method as well, but this package requires redefinition for DB backed
in Django settings which sometimes is not possible.

django-pg-upsert is designed to solve only one problem (depends only from django) and is not a Swiss knife.
