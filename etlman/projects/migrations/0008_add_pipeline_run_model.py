# Generated by Django 4.0.6 on 2022-11-01 18:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_add_celery_schedule_to_pipeline_schedule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pipelineschedule',
            name='unit',
            field=models.CharField(blank=True, choices=[('days', 'Days'), ('hours', 'Hours'), ('minutes', 'Minutes'), ('seconds', 'Seconds')], max_length=56, null=True),
        ),
        migrations.CreateModel(
            name='PipelineRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField()),
                ('ended_at', models.DateTimeField()),
                ('output', models.JSONField()),
                ('pipeline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pipeline_runs', to='projects.pipeline')),
            ],
        ),
    ]