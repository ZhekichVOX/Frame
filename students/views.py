"""Страницы студентов: список и карточка студента."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.students import find_student_by_id
from models.subgroups import find_student_subgroup
from storage import load_all


def students(request: HttpRequest) -> HttpResponse:
    """Страница /students/: студенты по группам и алфавиту."""
    _, students_list, subgroups_list = load_all()
    ordered = sorted(
        students_list,
        key=lambda s: (s.group.course, s.group.name, s.name),
    )
    items = [
        {
            "student": student,
            "subgroup": find_student_subgroup(subgroups_list, student),
        }
        for student in ordered
    ]
    return render(request, "students/student_list.html", {"items": items})


def student_detail(request: HttpRequest, student_id: int) -> HttpResponse:
    """Страница /students/<id>/: группа и подгруппа студента."""
    _, students_list, subgroups_list = load_all()
    student = find_student_by_id(students_list, student_id)

    subgroup = None
    if student is not None:
        subgroup = find_student_subgroup(subgroups_list, student)

    return render(
        request,
        "students/student_detail.html",
        {"student": student, "subgroup": subgroup},
        status=404 if student is None else 200,
    )
