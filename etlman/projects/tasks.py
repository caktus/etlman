from celery import shared_task

from etlman.projects.models import Pipeline


@shared_task
def run_pipeline(pipeline_id):
    pipeline = Pipeline.objects.get(id=pipeline_id)
    print(f"Pipelinerunning on celery - Pipeline_id: {pipeline.id}")

    # step = Step.objects.get(id=step_id)
    # print(f"Step running on celery - Pipeline_id: {step.id}")
    # step.run_script()
