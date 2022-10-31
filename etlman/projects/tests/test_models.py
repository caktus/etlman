import pytest

from etlman.backends.test_backend import TestBackend
from etlman.projects.models import Pipeline, PipelineRun
from etlman.projects.tests.factories import (
    DataInterfaceFactory,
    PipelineFactory,
    PipelineScheduleFactory,
    ProjectFactory,
    StepFactory,
)


@pytest.mark.django_db
class TestScriptForm:
    def test_django_model_str_methods(self):
        builded_object = DataInterfaceFactory.build()
        assert builded_object.name == str(builded_object)
        builded_object = ProjectFactory.build()
        assert builded_object.name == str(builded_object)
        builded_object = PipelineFactory.build()
        assert builded_object.name == str(builded_object)
        builded_object = StepFactory.build()
        assert builded_object.name == str(builded_object)


@pytest.mark.django_db
class TestPipelineModel:
    def test_run_pipeline_single_step(self):
        """
        Pipeline.run_pipeline() method creates the correct PipelineRun object in the database.
        """
        pipeline = Pipeline(name=PipelineFactory.build().name)
        pipeline.project = ProjectFactory()
        pipeline.save()  # Saved pipeline to avoid integrity error due to atomic transaction
        PipelineScheduleFactory(pipeline=pipeline)
        StepFactory(pipeline=pipeline)
        backend = TestBackend()
        pipeline.run_pipeline(backend=backend)
        PipelineRun.objects.count() == 1
        last_run_pipeline = PipelineRun.objects.all().first()
        assert pipeline.name == last_run_pipeline.pipeline.name
        assert pipeline.project == last_run_pipeline.pipeline.project

    def test_run_pipeline_multiple_steps(self):
        """
        Pipeline.run_pipeline() method creates the correct PipelineRun object in the database
        for a Pipeline with multiple Steps.
        """
        pipeline = Pipeline(name=PipelineFactory.build().name)
        pipeline.project = ProjectFactory()
        pipeline.save()  # Saved pipeline to avoid integrity error due to atomic transaction
        pipeline2 = Pipeline(name=PipelineFactory.build().name)
        pipeline2.project = ProjectFactory()
        pipeline2.save()
        pipeline3 = Pipeline(name=PipelineFactory.build().name)
        pipeline3.project = ProjectFactory()
        pipeline3.save()
        PipelineScheduleFactory(pipeline=pipeline)
        StepFactory(pipeline=pipeline)
        StepFactory(pipeline=pipeline2)
        StepFactory(pipeline=pipeline3)
        backend = TestBackend()
        pipeline.run_pipeline(backend=backend)
        pipeline2.run_pipeline(backend=backend)
        pipeline3.run_pipeline(backend=backend)
        PipelineRun.objects.count() == 3
