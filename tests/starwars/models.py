from django.db import models


class Pet(models.Model):
    name = models.CharField(max_length=30, unique=True)
    age = models.PositiveIntegerField()
