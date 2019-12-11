from django.db import models
from django_pg_upsert import Manager as PgManager


class Manager(PgManager):
    pass


class Pet(models.Model):
    name = models.CharField(max_length=30, unique=True)
    alias_name = models.CharField(blank=True, null=True, max_length=30)
    age = models.PositiveIntegerField()

    objects = Manager()
