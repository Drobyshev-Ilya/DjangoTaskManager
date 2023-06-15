from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='begin_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
