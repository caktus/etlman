from celery import shared_task

from etlman.projects.models import Pipeline


@shared_task
def run_pipeline(pipeline_id):
    pipeline = Pipeline.objects.get(id=pipeline_id)
    print(f"Running Pipeline - {pipeline_id=}")
    pipeline.run_pipeline()
