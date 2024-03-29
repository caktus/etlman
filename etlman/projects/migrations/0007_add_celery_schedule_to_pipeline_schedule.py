# Generated by Django 4.0.6 on 2022-10-25 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_beat', '0016_alter_crontabschedule_timezone'),
        ('projects', '0006_add_pipelineschedule_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pipelineschedule',
            name='frequency',
        ),
        migrations.AddField(
            model_name='pipelineschedule',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_celery_beat.periodictask'),
        ),
        migrations.AlterField(
            model_name='pipelineschedule',
            name='unit',
            field=models.CharField(blank=True, choices=[('days', 'Days'), ('hours', 'Hours'), ('minutes', 'Minutes'), ('seconds', 'Seconds'), ('microseconds', 'Microseconds')], max_length=56, null=True),
        ),
        migrations.AlterField(
            model_name='step',
            name='pipeline',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='projects.pipeline'),
        ),
    ]
