from django.db import models

# Create your models here.
class Projects(models.Model):
    # collaborators 
    name = models.CharField(max_length=256)
    description = models.TextField()

class DataInterface(models.Model):
    name = models.CharField(max_length=256)
    connection_string = models.CharField(max_length=1024)

class Pipeline(models.Model):
    name = models.CharField(max_length=256)
    # steps

class Step(models.Model):
    name = models.CharField(max_length=256) # file name
    script = models.TextField() # payload
