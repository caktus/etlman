import datetime
import json

import pytz
from django.db import models, transaction
from django_celery_beat.models import PERIOD_CHOICES, IntervalSchedule, PeriodicTask

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

    def run_pipeline(self, backend=None):
        if backend is None:
            backend = get_backend()
        output = {
            "pipeline_id": self.pk,
            "steps": [],
        }
        for step in self.steps.order_by("step_order").all():
            returncode, stdout, stderr = step.run_script(backend=backend)
            output["steps"].append(
                {
                    "step_id": step.pk,
                    "returncode": returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                }
            )
        PipelineRun.objects.create(
            pipeline=self,
            started_at=self.schedule.task.start_time,
            ended_at=self.schedule.task.last_run_at,
            output=output,
        )

    def __str__(self):
        return self.name


class Step(models.Model):
    LANGUAGE_CHOICES = [("python", "Python"), ("r", "R")]

    pipeline = models.ForeignKey(
        Pipeline, on_delete=models.CASCADE, related_name="steps"
    )
    name = models.CharField(max_length=256)
    language = models.CharField(max_length=56, choices=LANGUAGE_CHOICES)
    script = models.TextField()
    step_order = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def run_script(self, backend=None):
        if backend is None:
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
    task = models.ForeignKey(
        PeriodicTask, on_delete=models.CASCADE, null=True, blank=True
    )
    pipeline = models.OneToOneField(
        Pipeline, related_name="schedule", on_delete=models.CASCADE
    )
    start_date = models.DateField()
    start_time = models.TimeField()
    time_zone = models.CharField(max_length=56, choices=TIMEZONES)
    interval = models.IntegerField(blank=True, null=True)
    unit = models.CharField(
        max_length=56, blank=True, null=True, choices=PERIOD_CHOICES
    )
    published = models.BooleanField(default=False)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Celery Tasks - to create a periodic task executing at an interval, first
        # create the IntervalSchedule then a PeriodicTask or CrontabSchedule.
        # https://django-celery-beat.readthedocs.io/en/latest/#:~:text=To%20create%20a%20periodic%20task%20executing,%3E%3E%3E
        task_datetime = datetime.datetime.combine(
            self.start_date,
            self.start_time,
            tzinfo=pytz.timezone(self.time_zone),
        )
        interval_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=self.interval,
            period=self.unit,
        )
        task_params = dict(
            name=self.pipeline.name,
            task="etlman.projects.tasks.run_pipeline",
            kwargs=json.dumps(
                {
                    "pipeline_id": self.pipeline.id,
                }
            ),
            interval=interval_schedule,
            start_time=task_datetime,
            enabled=self.published,
        )
        if self.task:
            PeriodicTask.objects.filter(pk=self.task.pk).update(**task_params)
        else:
            self.task = PeriodicTask.objects.create(**task_params)
        super().save(*args, **kwargs)


class PipelineRun(models.Model):
    pipeline = models.ForeignKey(
        Pipeline, on_delete=models.CASCADE, related_name="pipeline_runs"
    )
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    output = models.JSONField()
