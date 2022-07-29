import pytest

from etlman.projects.forms import StepForm
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
