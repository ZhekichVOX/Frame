"""Страницы подгрупп: список и карточка подгруппы."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.subgroups import find_subgroup_by_id
from storage import load_all


def subgroups(request: HttpRequest) -> HttpResponse:
    """Страница /subgroups/: все сформированные подгруппы."""
    _, _, subgroups_list = load_all()
    ordered = sorted(subgroups_list, key=lambda s: (s.group.name, s.number))
    return render(
        request, "subgroups/subgroup_list.html", {"subgroups": ordered}
    )


def subgroup_detail(request: HttpRequest, subgroup_id: int) -> HttpResponse:
    """Страница /subgroups/<id>/: состав подгруппы."""
    _, _, subgroups_list = load_all()
    subgroup = find_subgroup_by_id(subgroups_list, subgroup_id)
    return render(
        request,
        "subgroups/subgroup_detail.html",
        {"subgroup": subgroup},
        status=404 if subgroup is None else 200,
    )
