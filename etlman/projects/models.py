from django.db import models

from etlman.users.models import User


class Project(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    collaborators = models.ManyToManyField(User, through="UserRole")


class UserRole(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class DataInterface(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    connection_string = models.CharField(max_length=1024)


class Pipeline(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)


class Step(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)  # file name
    script = models.TextField()  # payload




"""
  File "/home/victor/Code/caktus/etlman/env/lib/python3.10/site-packages/django/db/backends/utils.py", line 82, in _execute
    return self.cursor.execute(sql)
  File "/home/victor/Code/caktus/etlman/env/lib/python3.10/site-packages/django/db/backends/sqlite3/base.py", line 421, in execute
    return Database.Cursor.execute(self, query)
sqlite3.OperationalError: no such table: django_site_id_seq

The above exception was the direct cause of the following exception:
"""