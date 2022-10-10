import pytz
from django.db import models
from django_celery_beat.models import PERIOD_CHOICES, PeriodicTask

from etlman.backends import get_backend
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

    def run_script(self):
        backend = get_backend()
        return backend.execute_script(self.language, self.script)

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


class PipelineSchedule(models.Model):
    TIMEZONES = [(tz, tz) for tz in pytz.common_timezones]
    # FREQUENCY_INTERVALS = [
    #     ("no_repeat", "Does not repeat"),
    #     ("every", "Every..."),
    #     ("every_other", "Every other..."),
    #     ("hourly", "Hourly..."),
    #     ("daily", "Daily..."),
    #     ("weekly", "Weekly..."),
    #     ("monthly", "Monthly..."),
    #     ("annually", "Annually..."),
    # ]
    # UNIT_INTERVALS = [
    #     ("seconds", "Second(s)"),
    #     ("minutes", "Minute(s)"),
    #     ("hours", "Hour(s)"),
    #     ("days", "Day(s)"),
    #     ("weeks", "Week(s)"),
    #     ("months", "Month(s)"),
    #     ("years", "Year(s)"),
    # ]
    task = models.ForeignKey(
        PeriodicTask, on_delete=models.CASCADE, null=True, blank=True
    )
    pipeline = models.OneToOneField(
        Pipeline, related_name="schedule", on_delete=models.CASCADE
    )
    start_date = models.DateField()
    start_time = models.TimeField()
    time_zone = models.CharField(max_length=56, choices=TIMEZONES)
    frequency = models.CharField(max_length=56, choices=PERIOD_CHOICES)
    interval = models.IntegerField(blank=True, null=True)
    unit = models.CharField(
        max_length=56, blank=True, null=True, choices=PERIOD_CHOICES
    )
    published = models.BooleanField(default=False)
