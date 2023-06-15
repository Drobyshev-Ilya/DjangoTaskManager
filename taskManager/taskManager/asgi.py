"""
Конфигурация ASGI.

Он предоставляет вызываемый ASGI как переменную уровня модуля с именем «application».

Дополнительные сведения об этом файле см.
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskManager.settings')

application = get_asgi_application()
