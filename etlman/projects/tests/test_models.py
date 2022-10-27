import pytest

from etlman.backends.test_backend import TestBackend
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
        assert builded_object.name == str(builded_object)
        builded_object = StepFactory.build()
        assert builded_object.name == str(builded_object)


@pytest.mark.django_db
class TestPipelineModel:
    def test_run_pipeline_single_step(self):
        """
        Pipeline.run_pipeline() method creates the correct PipelineRun object in the database.
        """
        pipeline = PipelineFactory()
        StepFactory()
        backend = TestBackend()
        pipeline.run_pipeline(backend=backend)
        # assertions to check for:
        # - count of PipelineRuns
        # - get the one PipelineRun that was created
        # - check all attributes on the PipelineRun object

    def test_run_pipeline_multiple_steps(self):
        """
        Pipeline.run_pipeline() method creates the correct PipelineRun object in the database
        for a Pipeline with multiple Steps.
        """
        # Same as above, with 2 or 3 steps.
