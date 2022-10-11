from celery import shared_task

from etlman.projects.models import Step


@shared_task
def run_pipeline(step_id):
    step = Step.objects.get(id=step_id)
    print(f"Running Script - Step_id: {step.id}")
    step.run_script()
