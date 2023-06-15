from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_auto_20211129_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timestamp',
            name='begin_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
