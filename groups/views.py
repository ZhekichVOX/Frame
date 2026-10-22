"""Страницы групп: список и карточка группы."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.groups import find_group_by_id, sort_groups
from models.students import get_group_students
from models.subgroups import get_group_subgroups, is_group_split
from storage import load_all


def groups(request: HttpRequest) -> HttpResponse:
    """Страница /groups/: группы по курсу с числом студентов и статусом."""
    groups_list, students_list, subgroups_list = load_all()
    items = [
        {
            "group": group,
            "students_count": len(get_group_students(students_list, group)),
            "is_split": is_group_split(subgroups_list, group),
        }
        for group in sort_groups(groups_list)
    ]
    return render(request, "groups/group_list.html", {"items": items})


def group_detail(request: HttpRequest, group_id: int) -> HttpResponse:
    """Страница /groups/<id>/: состав группы и её подгруппы."""
    groups_list, students_list, subgroups_list = load_all()
    group = find_group_by_id(groups_list, group_id)

    context = {
        "group": group,
        "students": [],
        "subgroups": [],
        "is_split": False,
    }
    if group is not None:
        context["students"] = get_group_students(students_list, group)
        context["subgroups"] = get_group_subgroups(subgroups_list, group)
        context["is_split"] = is_group_split(subgroups_list, group)

    return render(
        request,
        "groups/group_detail.html",
        context,
        status=404 if group is None else 200,
    )
