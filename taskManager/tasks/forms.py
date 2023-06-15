from django import forms
from tasks.models import Task, Timestamp

#Переопределить dateinput и datetimeinput, чтобы django мог читать html-селекторы date и datetime.
class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'
    
class DateInput(forms.DateInput):
    input_type = 'date'

#Добавить новую задачу
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["task_name", "task_description", "project", "status"]
        
class UpdateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["task_name", "task_description", "project"]
        
class StatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["status"]

#Фильтр задач в списке меток времени        
class TimestampSearchForm(forms.Form):
    task_name = forms.CharField(label="id_task_name", max_length=100)

#Обновить форму временной метки
class UpdateTsForm(forms.ModelForm):
    class Meta:
        model = Timestamp
        fields = ["begin_time", "end_time"]
        widgets = {'begin_time' : DateTimeInput(), 'end_time' : DateTimeInput()}   
        
#Селектор недели/месяца      
class DateFilter(forms.Form):
    day = forms.DateField(label="date_filter", widget=DateInput())
