"""Конфигурация URL диспетчера задач

Список `urlpatterns` направляет URL-адреса в представления. Для получения дополнительной информации см.:
     https://docs.djangoproject.com/en/3.2/topics/http/urls/
Примеры:
Представления функций
     1. Добавить импорт: из представлений импорта my_app
     2. Добавить URL-адрес в urlpatterns: path('', views.home, name='home')
Представления на основе классов
     1. Добавить импорт: from other_app.views import Home
     2. Добавить URL-адрес в шаблоны URL-адресов: path('', Home.as_view(), name='home')
Включение другой конфигурации URL
     1. Импорт функции include(): из django.urls import include, path
     2. Добавить URL-адрес в urlpatterns: path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('add_task', views.new),
    path('show_tasks', views.show_tasks),
    path('edit_task/<int:id>', views.edit_task),
    path('update_task/<int:id>', views.update_task),
    path('delete_task/<int:id>', views.kill_task),
    path('status/<int:id>', views.status),
    path('timestamp/<int:id>', views.timestamp),
    path('show_timestamps', views.show_timestamps),
    path('timestamp_search', views.timestamp_search),
    path('delete_timestamp/<int:id>', views.delete_timestamp),
    path('edit_timestamp/<int:id>', views.edit_timestamp),
    path('update_timestamp/<int:id>', views.update_timestamp),
	  path('show_time_dashboard', views.show_time_dashboard),
    path('show_task_dashboard', views.show_task_dashboard),
	  re_path(r'^$', views.index, name='index'),
]
