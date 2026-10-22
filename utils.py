"""Вспомогательные функции: учебный год, безопасный ввод, декоратор."""
from datetime import date
from functools import wraps
from typing import Any, Callable


def handle_errors(action: Callable[..., None]) -> Callable[..., None]:
    """Декоратор: сообщение вместо падения при ValueError в действии меню.

    functools.wraps сохраняет имя и docstring исходной функции.
    """
    @wraps(action)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            action(*args, **kwargs)
        except ValueError as error:
            print(f"Ошибка: {error}")

    return wrapper


def get_academic_year(today: date) -> str:
    """Вернуть учебный год в формате '2026/2027' для переданной даты."""
    if today.month >= 9:
        return f"{today.year}/{today.year + 1}"
    return f"{today.year - 1}/{today.year}"


def input_int(
    prompt: str,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Запросить целое число; при ошибке ввода повторять запрос."""
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print("Нужно ввести целое число")
            continue
        if min_value is not None and value < min_value:
            print(f"Число должно быть не меньше {min_value}")
            continue
        if max_value is not None and value > max_value:
            print(f"Число должно быть не больше {max_value}")
            continue
        return value


def input_text(prompt: str) -> str:
    """Запросить непустую строку; при пустом вводе повторять запрос."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("Значение не может быть пустым")
