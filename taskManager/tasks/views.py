from django.shortcuts import render, redirect
from tasks.forms import TaskForm, UpdateTaskForm, StatusForm, TimestampSearchForm, UpdateTsForm, DateFilter
from tasks.models import Task, Timestamp
from django.utils import timezone
from collections import defaultdict
from django.db.models import Sum
from datetime import timedelta, date, datetime
import pytz
import math

# Создание views.
#При входе на главную страницу (127.0.0.1/8000/) автоматически перенаправляется на страницу show_tasks
def index(request):
	return redirect("/show_tasks")
    
#добавить страницу задачи
def new(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('/show_tasks')
            except:
                pass
    else:
        form = TaskForm()
    return render(request,'add_task.html',{'form':form})

    
def show_tasks(request):
    tasks = Task.objects.all().order_by('-id')
    return render(request, "show_tasks.html", {'tasks':tasks})

#показать страницу редактирования задачи   
def edit_task(request, id):
    tasks = Task.objects.get(id=id)
    form = UpdateTaskForm(initial={'task_name':tasks.task_name, 'task_description':tasks.task_description, 'project':tasks.project})
    return render(request, "edit_task.html", {'tasks':tasks, 'form':form})

#редактирование задачи и обновление бд
def update_task(request, id):
    tasks = Task.objects.get(id=id)
    if request.method == "POST":
        form = UpdateTaskForm(request.POST, instance=tasks)
        if form.is_valid():
            try:
                form.save()
                return redirect('/show_tasks')
            except:
                pass
    else:
        form = UpdateTaskForm(initial={'task_name':tasks.task_name, 'task_description':tasks.task_description, 'project':tasks.project})   
    return render(request, "edit_task.html", {'tasks':tasks, 'form':form})

#удалить задачу
def kill_task(request, id):
    task = Task.objects.get(id=id)
    task.delete()
    return redirect("/show_tasks")

#обновить статус задачи
def status(request, id):
    tasks = Task.objects.get(id=id)
    form = StatusForm(request.POST, instance=tasks)
    form.save()
    return redirect("/show_tasks")

#Создать новую временную метку для задачи    
def timestamp(request, id):
    task = Task.objects.get(id=id)
    #Если состояние таймера «Запустить таймер», задача не имеет активной временной метки, поэтому установливается begin_time и состояние таймера меняется на «Остановить таймер».
    if(task.timer_state == 'Запустить таймер'):
        task.begin_time = timezone.now()
        task.timer_state = "Остановить таймер"
        task.save()
    #Если состояние таймера «Остановить таймер», метка времени уже запущена, создаётся новый объект метки времени и состояние таймера меняется на «Запустить таймер».
    else:
        new_ts = Timestamp(task=task, begin_time=task.begin_time, end_time=timezone.now())
        task.timer_state = "Запустить таймер"
        task.save()
        new_ts.save()
    return redirect("/show_tasks")

#Фильтр задач в списке меток времени    
def timestamp_search(request):
    form = TimestampSearchForm(request.POST)
    if form.is_valid():
        timestamps = Timestamp.objects.filter(task__task_name=form.cleaned_data['task_name']).order_by('-begin_time')
        return render(request, "show_timestamps.html", {'timestamps':timestamps})
    return redirect("/show_timestamps")
    
def show_timestamps(request):
    timestamps = Timestamp.objects.all().order_by('-id')
    return render(request, "show_timestamps.html", {'timestamps':timestamps})

def delete_timestamp(request, id):
    ts = Timestamp.objects.get(id=id)
    # Попытки сохранить поиск. Если запрос пришел из show_timestamps, он пришел из полного списка временных меток, поэтому возвращается полный список
    if "show_timestamps" in request.META['HTTP_REFERER']:  
        ts.delete()
        return redirect("/show_timestamps")
    # в противном случае повторить поиск задачи и вернуть отфильтрованный список
    else:
        ts.delete()
        timestamps = Timestamp.objects.filter(task__task_name=ts.task.task_name).order_by('-begin_time')
        return render(request, "show_timestamps.html", {'timestamps':timestamps})

#тот же процесс, что и edit_task
def edit_timestamp(request, id):
    timestamp=Timestamp.objects.get(id=id)
    form = UpdateTsForm()
    return render(request, 'edit_timestamp.html', {'timestamp':timestamp, 'form':form})
    
#Поскольку редактирование, обновление — это двухэтапный процесс, нельзя использовать HTTP_REFERER для сохранения поиска, поэтому редактирование всегда будет возвращать полный Журнал активности.
def update_timestamp(request, id):
    timestamp = Timestamp.objects.get(id=id)
    if request.method == 'POST':
        form = UpdateTsForm(request.POST, instance=timestamp)
        if form.is_valid() and form.cleaned_data['begin_time'] < form.cleaned_data['end_time']:
            try:
                form.save()
                return redirect("/show_timestamps")
            except:
                pass
    form = UpdateTsForm()
    return render(request, "edit_timestamp.html", {'form':form, 'timestamp':timestamp})

def show_time_dashboard(request):
    tasks = Task.objects.all().order_by('-id')
    ts_total = {}
    ts_week = {}
    ts_month = {}
    if request.method == 'POST':
        #Если указана дата, извлечь год, месяц и начало недели
        date_form = DateFilter(request.POST)
        if date_form.is_valid():
            year = date_form.cleaned_data['day'].year
            month = date_form.cleaned_data['day'].month
            week_start = date_form.cleaned_data['day'] - timedelta(days=date_form.cleaned_data['day'].weekday())
    #В противном случае используется сегодняшняя дата
    else:
        date_form = DateFilter()
        year = date.today().year
        month = date.today().month
        week_start = date.today() - timedelta(days=date.today().weekday())
    week_end = week_start + timedelta(days=6)
    #Рассчитать начало и конец недели и месяца как локализованную дату и время. Это упрощает вычисления со значениями временных меток, поскольку все они одного типа.
    #Также исправляет ошибку, из-за которой, поскольку даты и время всегда хранятся в базе данных как время UTC, datetime.day будет отключен на 1, если дата и время выпадают поздно ночью или рано утром из-за изменения времени.
    week_start_time = pytz.timezone('US/Eastern').localize(datetime.combine(week_start, datetime.min.time()))
    week_end_time = pytz.timezone('US/Eastern').localize(datetime.combine(week_end, datetime.max.time()))
    month_start_time = pytz.timezone('US/Eastern').localize(datetime(year, month, 1, 0, 0))
    month_end_time = pytz.timezone('US/Eastern').localize(datetime((year+1 if month==12 else year), (1 if month==12 else month+1), 1, 0, 0))
    #Поиск проектов для фильтрации
    projects = set()
    for task in tasks:
        timestamps = Timestamp.objects.filter(task__id=task.id)
        projects.add(task.project)
        #Общее время на каждую задачу
        ts_total[task.id] = 0
        #Время, потраченное на задачу на этой неделе
        ts_week[task.id] = 0
        #Время, потраченное на задачу в этом месяце
        ts_month[task.id] = 0
        for timestamp in timestamps:
            ts_total[task.id] += timestamp.elapsed_time()
            #Если временная метка начинается и заканчивается в течение недели, вся временная метка добавляется к еженедельному времени.
            if timestamp.begin_time >= week_start_time and timestamp.end_time <= week_end_time:
                ts_week[task.id] += timestamp.elapsed_time()
            #Если Журнал активности начинаются до недели, но заканчиваются в течение недели, добавляется только время между началом недели и концом временной метки.
            if timestamp.begin_time < week_start_time and timestamp.end_time <= week_end_time and timestamp.end_time > week_start_time:
                ts_week[task.id] += math.floor((timestamp.end_time - week_start_time).total_seconds()/60)
            #Если временная метка начинается в течение недели, но заканчивается после недели, добавляется только время от начала временной метки до конца недели.
            if timestamp.begin_time <= week_end_time and timestamp.begin_time >= week_start_time and timestamp.end_time > week_end_time:
                ts_week[task.id] += math.floor((week_end_time - timestamp.begin_time).total_seconds()/60) + 1 #Нужен +1, потому что week_end_time в 23:59, нужно добавить последнюю минуту
            #Если отметка времени начинается до недели и заканчивается после недели, добавляется вся неделя
            if timestamp.begin_time < week_start_time and timestamp.end_time > week_end_time:
                ts_week[task.id] += math.floor((week_end_time - week_start_time).total_seconds()/60) + 1
            #Та же логика для месяца, что и для недели
            if timestamp.begin_time >= month_start_time and timestamp.end_time <= month_end_time:
                ts_month[task.id] += timestamp.elapsed_time()
            if timestamp.begin_time < month_start_time and timestamp.end_time <= month_end_time and timestamp.end_time > month_start_time:
                ts_month[task.id] += math.floor((timestamp.end_time - month_start_time).total_seconds()/60)
            if timestamp.begin_time >= month_start_time and timestamp.end_time > month_end_time and timestamp.begin_time < month_end_time:
                ts_month[task.id] += math.floor((month_end_time - timestamp.begin_time).total_seconds()/60)
            if timestamp.begin_time < month_start_time and timestamp.end_time > month_end_time:
                ts_month[task.id] += math.floor((month_end_time - month_start_time).total_seconds()/60)
    
    p_total = {}
    p_week = {}
    p_month = {}
    #Выполняет тот же процесс, что и для задач, но циклически перебирает разные проекты.
    for project in projects:
        timestamps = Timestamp.objects.filter(task__project=project)
        p_total[project] = 0
        p_week[project] = 0
        p_month[project] = 0
        for timestamp in timestamps:
            p_total[project] += timestamp.elapsed_time()
            if timestamp.begin_time >= week_start_time and timestamp.end_time <= week_end_time:
                p_week[project] += timestamp.elapsed_time()
            if timestamp.begin_time < week_start_time and timestamp.end_time <= week_end_time and timestamp.end_time > week_start_time:
                p_week[project] += math.floor((timestamp.end_time - week_start_time).total_seconds()/60)
            if timestamp.begin_time <= week_end_time and timestamp.begin_time >= week_start_time and timestamp.end_time > week_end_time:
                p_week[project] += math.floor((week_end_time - timestamp.begin_time).total_seconds()/60) + 1
            if timestamp.begin_time < week_start_time and timestamp.end_time > week_end_time:
                p_week[project] += math.floor((week_end_time - week_start_time).total_seconds()/60) + 1
          
            if timestamp.begin_time >= month_start_time and timestamp.end_time <= month_end_time:
                p_month[project] += timestamp.elapsed_time()
            if timestamp.begin_time < month_start_time and timestamp.end_time <= month_end_time and timestamp.end_time > month_start_time:
                p_month[project] += math.floor((timestamp.end_time - month_start_time).total_seconds()/60)
            if timestamp.begin_time >= month_start_time and timestamp.end_time > month_end_time and timestamp.begin_time < month_end_time:
                p_month[project] += math.floor((month_end_time - timestamp.begin_time).total_seconds()/60)
            if timestamp.begin_time < month_start_time and timestamp.end_time > month_end_time:
                p_month[project] += math.floor((month_end_time - month_start_time).total_seconds()/60)
            
    return render(request, "show_time_dashboard.html", {
        'tasks':tasks, 
        'ts_total':ts_total, 
        'date_form':date_form, 
        'ts_week':ts_week, 
        'ts_month':ts_month, 
        'week_start':week_start,
        'month':datetime.strptime(str(month), "%m").strftime("%B"),
        'projects':projects,
        'p_total':p_total,
        'p_week':p_week,
        'p_month':p_month,
    })
  
def show_task_dashboard(request):
    tasks = Task.objects.all().order_by('-id')
    ts_total = {}
    ts_week = {}
    ts_month = {}
    #Та же логика даты, что и в show_time_dasboard
    if request.method == 'POST':
        date_form = DateFilter(request.POST)
        if date_form.is_valid():
            year = date_form.cleaned_data['day'].year
            month = date_form.cleaned_data['day'].month
            week_start = date_form.cleaned_data['day'] - timedelta(days=date_form.cleaned_data['day'].weekday())
    else:
        date_form = DateFilter()
        year = date.today().year
        month = date.today().month
        week_start = date.today() - timedelta(days=date.today().weekday())
    week_end = week_start + timedelta(days=6)
    week_start_time = pytz.timezone('US/Eastern').localize(datetime.combine(week_start, datetime.min.time()))
    week_end_time = pytz.timezone('US/Eastern').localize(datetime.combine(week_end, datetime.max.time()))
    month_start_time = pytz.timezone('US/Eastern').localize(datetime(year, month, 1, 0, 0))
    month_end_time = pytz.timezone('US/Eastern').localize(datetime((year+1 if month==12 else year), (1 if month==12 else month+1), 1, 0, 0))
    ts_total_avg = {}
    ts_week_avg = {}
    ts_month_avg = {}
    ts_total_pct = {}
    ts_week_pct = {}
    ts_month_pct = {}
    #Подсчет общего времени, затраченного на % от потраченного времени
    total_time = 0
    total_week_time = 0
    total_month_time = 0    
    for task in tasks:
        timestamps = Timestamp.objects.filter(task__id=task.id)
        ts_total[task.id] = 0
        ts_week[task.id] = 0
        ts_month[task.id] = 0
        #Подсчет общего количества временных меток для задачи для средней продолжительности временной метки
        ts_total_count = 0
        #Подсчет общего количества временных меток за неделю
        ts_week_count = 0
        #Подсчет общего количества временных меток за месяц
        ts_month_count = 0
        #Вся та же логика, что и у show_time_dashboard, но также обновляются счетчики временных меток и счетчики времени.
        for timestamp in timestamps:
            ts_total[task.id] += timestamp.elapsed_time()
            ts_total_count += 1
            total_time += timestamp.elapsed_time()
            if timestamp.begin_time >= week_start_time and timestamp.end_time <= week_end_time:
                ts_week[task.id] += timestamp.elapsed_time()
                ts_week_count += 1
                total_week_time += timestamp.elapsed_time()
            if timestamp.begin_time < week_start_time and timestamp.end_time <= week_end_time and timestamp.end_time > week_start_time:
                ts_week[task.id] += math.floor((timestamp.end_time - week_start_time).total_seconds()/60)
                ts_week_count += 1
                total_week_time += math.floor((timestamp.end_time - week_start_time).total_seconds()/60)
            if timestamp.begin_time <= week_end_time and timestamp.begin_time >= week_start_time and timestamp.end_time > week_end_time:
                ts_week[task.id] += math.floor((week_end_time - timestamp.begin_time).total_seconds()/60) + 1
                ts_week_count += 1
                total_month_time += math.floor((week_end_time - timestamp.begin_time).total_seconds()/60) + 1
            if timestamp.begin_time < week_start_time and timestamp.end_time > week_end_time:
                ts_week[task.id] += math.floor((week_end_time - week_start_time).total_seconds()/60) + 1
                ts_week_count += 1
                total_week_time += math.floor((week_end_time - week_start_time).total_seconds()/60) + 1
          
            if timestamp.begin_time >= month_start_time and timestamp.end_time <= month_end_time:
                ts_month[task.id] += timestamp.elapsed_time()
                ts_month_count += 1
                total_month_time += timestamp.elapsed_time()
            if timestamp.begin_time < month_start_time and timestamp.end_time <= month_end_time and timestamp.end_time > month_start_time:
                ts_month[task.id] += math.floor((timestamp.end_time - month_start_time).total_seconds()/60)
                ts_month_count += 1
                total_month_time += math.floor((timestamp.end_time - month_start_time).total_seconds()/60)
            if timestamp.begin_time >= month_start_time and timestamp.end_time > month_end_time and timestamp.begin_time < month_end_time:
                ts_month[task.id] += math.floor((month_end_time - timestamp.begin_time).total_seconds()/60)
                ts_month_count += 1
                total_month_time += math.floor((month_end_time - timestamp.begin_time).total_seconds()/60)
            if timestamp.begin_time < month_start_time and timestamp.end_time > month_end_time:
                ts_month[task.id] += math.floor((month_end_time - month_start_time).total_seconds()/60)
                ts_month_count += 1
                total_month_time += math.floor((month_end_time - month_start_time).total_seconds()/60)
      
        #Вычисление средних значений длины метки времени, если ts_XXXX_count == 0, меток времени для этого периода нет, поэтому возвращается 0
        ts_total_avg[task.id] =  round(ts_total[task.id] / ts_total_count, 1) if ts_total_count else 0
        ts_week_avg[task.id] = round(ts_week[task.id] / ts_week_count, 1) if ts_week_count else 0
        ts_month_avg[task.id] = round(ts_month[task.id] / ts_month_count, 1) if ts_month_count else 0
        
    
    #Вычисление процента времени, затраченного на каждую задачу за каждый период времени
    for task in tasks:
        ts_total_pct[task.id] = round((ts_total[task.id] / total_time)*100) if total_time else 0
        ts_week_pct[task.id] = round((ts_week[task.id] / total_week_time)*100) if total_week_time else 0
        ts_month_pct[task.id] = round((ts_month[task.id] / total_month_time)*100) if total_month_time else 0
        
    return render(request, "show_task_dashboard.html", {
        'ts_total_avg':ts_total_avg,
        'ts_week_avg':ts_week_avg,
        'ts_month_avg':ts_month_avg,
        'date_form':date_form,
        'week_start':week_start,
        'month':datetime.strptime(str(month), "%m").strftime("%B"),
        'tasks':tasks, 
        'ts_total_pct':ts_total_pct,
        'ts_week_pct':ts_week_pct,
        'ts_month_pct':ts_month_pct,
    })
        

