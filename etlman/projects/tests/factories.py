import datetime
import random

import factory
import factory.fuzzy
from django_celery_beat.models import MICROSECONDS, PERIOD_CHOICES

from etlman.projects import models
from etlman.users.tests.factories import UserFactory

UNITS = [
    (value, label) for value, label in PERIOD_CHOICES if value not in {MICROSECONDS}
]  # Units without microseconds


class ProjectFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    description = factory.Faker("sentence")

    class Meta:
        model = models.Project


class CollaboratorFactory(factory.django.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    user = factory.SubFactory(UserFactory)
    role = factory.Faker("pystr")

    class Meta:
        model = models.Collaborator


class DataInterfaceFactory(factory.django.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    name = factory.Faker("company")
    interface_type = factory.fuzzy.FuzzyChoice(
        [key for key, _ in models.DataInterface.INTERFACE_TYPE_CHOICES]
    )
    connection_string = factory.Faker("sentence")
    sql_query = factory.Faker("hostname")

    class Meta:
        model = models.DataInterface


class PipelineFactory(factory.django.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    name = factory.Faker("name")
    input = factory.SubFactory(DataInterfaceFactory)

    class Meta:
        model = models.Pipeline


class StepFactory(factory.django.DjangoModelFactory):
    pipeline = factory.SubFactory(PipelineFactory)
    name = factory.Faker("name")  # file name
    script = factory.Faker("pystr")  # payload
    step_order = factory.Sequence(lambda n: n)
    language = factory.fuzzy.FuzzyChoice(
        [key for key, _ in models.Step.LANGUAGE_CHOICES]
    )

    class Meta:
        model = models.Step


class PipelineScheduleFactory(factory.django.DjangoModelFactory):
    pipeline = factory.SubFactory(PipelineFactory)
    start_date = factory.Faker("date_this_year")
    start_time = factory.fuzzy.FuzzyAttribute(
        fuzzer=lambda: datetime.time(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
        )
    )
    interval = factory.Sequence(lambda n: n)
    unit = factory.fuzzy.FuzzyChoice([key for key, _ in UNITS])
    time_zone = factory.fuzzy.FuzzyChoice(
        [key for key, _ in models.PipelineSchedule.TIMEZONES]
    )
    published = True

    class Meta:
        model = models.PipelineSchedule


class PipelineRunFactory(factory.django.DjangoModelFactory):
    pipeline = factory.SubFactory(PipelineFactory)
    started_at = factory.Faker("date_time")
    ended_at = factory.Faker("date_time_this_month")
    output = factory.Faker("sentence")

    class Meta:
        model = models.PipelineRun
