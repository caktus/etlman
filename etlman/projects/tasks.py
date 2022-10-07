from celery import shared_task

from etlman.projects.models import Pipeline


@shared_task
def run_pipeline(pipeline_id):
    pipeline = Pipeline.objects.get(id=pipeline_id)
    print(f"Pipeline run on celery - Pipeline_id: {pipeline.id}")
