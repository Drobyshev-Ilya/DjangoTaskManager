from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_alter_timestamp_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timestamp',
            name='end_time',
            field=models.DateTimeField(),
        ),
    ]
