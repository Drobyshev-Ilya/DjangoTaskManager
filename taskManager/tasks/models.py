from django.db import models
import math

# Создание модели.
STATUSES = (
    ('в процессе', 'В процессе'),
    ('завершенный', 'Завершенный'),
)

TIMER_STATE = (
    ('Запустить таймер', 'запустить таймер'),
    ('Остановить таймер', 'остановить  таймер'),
)

class Timestamp(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True)
    begin_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField()
    
    def elapsed_time(self):
        return math.floor(((self.end_time - self.begin_time).total_seconds()/60))
    class Meta:
        db_table = "timestamps"

class Task(models.Model):
    task_name = models.CharField(max_length=100)
    task_description = models.TextField()
    timer_state = models.CharField(max_length=17, choices=TIMER_STATE, default='Запустить таймер') #Используется, чтобы определить, должна ли задача отслеживать время для создания метки времени.
    begin_time = models.DateTimeField(blank=True, null=True) #Требуется для записи времени начала временных меток. 
    project = models.CharField(max_length=100)
    status = models.CharField(max_length=11, choices=STATUSES, default='в процессе')
    class Meta:
        db_table = "tasks"
