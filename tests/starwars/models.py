from django.db import models
from django_pg_upsert import PgUpsertManager


class Human(models.Model):
    name = models.CharField(max_length=100)


class Pet(models.Model):
    name = models.CharField(max_length=30, unique=True)
    alias_name = models.CharField(blank=True, null=True, max_length=30)
    age = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PgUpsertManager()

    owner = models.ForeignKey(Human, on_delete=models.CASCADE, null=True)
