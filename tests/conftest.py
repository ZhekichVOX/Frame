import os

import django
import pytest
from django.test import Client
from django.test.utils import setup_test_environment

from models import Group, Student
from models.subgroups import create_subgroups
from storage import (
    save_groups,
    save_students,
    save_subgroups,
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subgroup_service.settings")
django.setup()
setup_test_environment()


@pytest.fixture
def group():
    return Group(1, "ИКБО-01-24", 2)


@pytest.fixture
def other_group():
    return Group(2, "ИВБО-02-23", 3)


@pytest.fixture
def make_students():
    """Фабрика: создать count студентов группы group."""
    def factory(group, count, start_id=1):
        return [
            Student(start_id + index, f"Студент {index + 1:02}", group)
            for index in range(count)
        ]

    return factory


@pytest.fixture
def web_data(tmp_path, monkeypatch, group, other_group, make_students):
    """Подменить файлы данных временными: 5 студентов, группа 1 разделена."""
    students = make_students(group, 5)
    subgroups = []
    create_subgroups(subgroups, students, group, 3)

    files = {
        "GROUPS_FILE": tmp_path / "groups.json",
        "STUDENTS_FILE": tmp_path / "students.json",
        "SUBGROUPS_FILE": tmp_path / "subgroups.json",
    }
    save_groups(files["GROUPS_FILE"], [group, other_group])
    save_students(files["STUDENTS_FILE"], students)
    save_subgroups(files["SUBGROUPS_FILE"], subgroups)
    for name, path in files.items():
        monkeypatch.setattr(f"storage.{name}", path)
    return {"files": files, "group": group, "students": students}


@pytest.fixture
def client(web_data):
    return Client()
