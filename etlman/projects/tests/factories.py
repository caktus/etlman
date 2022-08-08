import factory

from etlman.projects import models
from etlman.users.tests.factories import UserFactory


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
    name = factory.Faker("company")
    interface_type = factory.Faker("company_suffix")
    connection_string = factory.Faker("sentence")

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

    class Meta:
        model = models.Step
