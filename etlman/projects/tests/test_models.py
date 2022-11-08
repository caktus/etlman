import pytest

from etlman.backends.test_backend import TestBackend
from etlman.projects.models import PipelineRun
from etlman.projects.tests.factories import (
    DataInterfaceFactory,
    PipelineFactory,
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
        assert f"{builded_object.name}, pk: {builded_object.id}" == str(builded_object)
        builded_object = StepFactory.build()
        assert builded_object.name == str(builded_object)


@pytest.mark.django_db
class TestPipelineModel:
    def test_run_pipeline_single_step(self):
        """
        Pipeline.run_pipeline() method creates the correct PipelineRun object in the database.
        """
        pipeline = PipelineFactory()
        step = StepFactory(pipeline=pipeline)
        backend = TestBackend()
        pipeline.run_pipeline(backend=backend)
        PipelineRun.objects.count() == 1
        last_pipeline_run = PipelineRun.objects.all().first()
        assert pipeline == last_pipeline_run.pipeline
        assert last_pipeline_run.output["pipeline_id"] == pipeline.pk
        assert last_pipeline_run.output["steps"][0]["step_id"] == step.pk
        assert last_pipeline_run.output["steps"][0]["stdout"].startswith(
            TestBackend.STDOUT_MARKER
        )
        assert last_pipeline_run.output["steps"][0]["stderr"].startswith(
            TestBackend.STDERR_MARKER
        )

    def test_run_pipeline_multiple_steps(self):
        """
        Pipeline.run_pipeline() method creates the correct PipelineRun object in the database
        for a Pipeline with multiple Steps.
        """
        pipeline = PipelineFactory()
        step1 = StepFactory(pipeline=pipeline)
        step2 = StepFactory(pipeline=pipeline)
        step3 = StepFactory(pipeline=pipeline)
        backend = TestBackend()
        pipeline.run_pipeline(backend=backend)
        assert PipelineRun.objects.count() == 1
        last_pipeline_run = PipelineRun.objects.all().first()
        assert last_pipeline_run.output["pipeline_id"] == pipeline.pk
        assert len(last_pipeline_run.output["steps"]) == 3
        run_step_ids = {s["step_id"] for s in last_pipeline_run.output["steps"]}
        assert run_step_ids == {step1.id, step2.id, step3.id}
