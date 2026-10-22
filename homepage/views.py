"""Главная страница и страница ошибки 404."""
from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from storage import load_all
from utils import get_academic_year


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: описание сервиса и сводка по данным."""
    groups, students, subgroups = load_all()
    today = date.today()
    context = {
        "groups": groups,
        "students": students,
        "subgroups": subgroups,
        "today": today,
        "academic_year": get_academic_year(today),
    }
    return render(request, "homepage/index.html", context)


def page_not_found(
    request: HttpRequest, exception: Exception
) -> HttpResponse:
    """Обработчик handler404: адрес не совпал ни с одним маршрутом."""
    return render(request, "404.html", status=404)
