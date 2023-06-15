#!/usr/bin/env python
import os
import sys


def main():
    """Выполнение административных задач."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskManager.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
