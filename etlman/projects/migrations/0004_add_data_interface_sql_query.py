# Generated by Django 4.0.6 on 2022-08-31 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_alter_project_collaborators'),
    ]

    operations = [
        migrations.AddField(
            model_name='datainterface',
            name='sql_query',
            field=models.TextField(default='default_val'),
            preserve_default=False,
        ),
    ]