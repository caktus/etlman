from django.db import models

from etlman.users.models import User


class Project(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    collaborators = models.ManyToManyField(
        User, through="Collaborator", related_name="projects"
    )

    def __str__(self):
        return self.name


class Collaborator(models.Model):

    USER_ROLE_CHOICES = [
        ("admin", "Admin"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=USER_ROLE_CHOICES)


class DataInterface(models.Model):

    INTERFACE_TYPE_CHOICES = [("database", "Database")]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    interface_type = models.CharField(max_length=32, choices=INTERFACE_TYPE_CHOICES)
    connection_string = models.TextField()
    sql_query = models.TextField()

    def __str__(self):
        return self.name


class Pipeline(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    input = models.OneToOneField(DataInterface, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Step(models.Model):
    LANGUAGE_CHOICES = [("python", "Python"), ("r", "R")]

    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    language = models.CharField(max_length=56, choices=LANGUAGE_CHOICES)
    script = models.TextField()
    step_order = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="pipeline_step_order_unique",
                fields=(
                    "pipeline",
                    "step_order",
                ),
            )
        ]
