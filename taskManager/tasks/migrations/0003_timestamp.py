from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20211129_1919'),
    ]

    operations = [
        migrations.CreateModel(
            name='Timestamp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(auto_now=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.task')),
            ],
            options={
                'db_table': 'timestamps',
            },
        ),
    ]
