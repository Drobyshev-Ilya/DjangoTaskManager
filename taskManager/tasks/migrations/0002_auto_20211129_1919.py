from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='timer_state',
            field=models.CharField(choices=[('Start Timer', 'start timer'), ('Stop Timer', 'stop timer')], default='Start Timer', max_length=11),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('in progress', 'In Progress'), ('completed', 'Complete')], default='in progress', max_length=11),
        ),
    ]
