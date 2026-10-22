#!/usr/bin/env python
"""Утилита командной строки Django для административных задач."""
import os
import sys


def main() -> None:
    """Запустить административную команду."""
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "subgroup_service.settings"
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Установлен ли он и "
            "активировано ли виртуальное окружение? "
            "(pip install -r requirements.txt)"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
