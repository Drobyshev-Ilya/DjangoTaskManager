from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=100)),
                ('task_description', models.TextField()),
                ('project', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('in progress', 0), ('completed', 1)], default='in progress', max_length=11)),
            ],
            options={
                'db_table': 'tasks',
            },
        ),
    ]
