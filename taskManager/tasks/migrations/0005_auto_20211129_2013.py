from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_task_begin_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timestamp',
            name='begin_time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='timestamp',
            name='end_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
