from django.db import models

from etlman.users.models import User


class UserRole(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()


class Projects(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    collaborators = models.ManyToManyField(User, through=UserRole)


class DataInterface(models.Model):
    name = models.CharField(max_length=256)
    connection_string = models.CharField(max_length=1024)


class Script(models.Model):
    name = models.CharField(max_length=256)  # file name
    script = models.TextField()  # payload


class Step(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()


class Pipeline(models.Model):
    name = models.CharField(max_length=256)
    steps = models.ManyToManyField(Script, through=Step)
