from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_alter_timestamp_begin_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timestamp',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.task'),
        ),
    ]
