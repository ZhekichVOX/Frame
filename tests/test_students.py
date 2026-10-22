import pytest

from models import Student
from models.students import (
    add_student,
    find_student,
    find_student_by_id,
    get_group_students,
)


def test_student_creation_keeps_group_reference(group):
    student = Student(1, "Иванов П.М.", group)
    assert student.id == 1
    assert student.name == "Иванов П.М."
    assert student.group is group
    assert student.belongs_to(group)


def test_student_str(group):
    assert str(Student(1, "Иванов П.М.", group)) == "Иванов П.М. (ИКБО-01-24)"


def test_student_empty_name_forbidden(group):
    with pytest.raises(ValueError):
        Student(1, "  ", group)


def test_student_belongs_to_other_group(group, other_group):
    student = Student(1, "Иванов П.М.", group)
    assert not student.belongs_to(other_group)


def test_student_to_data_uses_group_id(group):
    student = Student(3, "Иванов П.М.", group)
    assert student.to_data() == {
        "id": 3,
        "name": "Иванов П.М.",
        "group_id": 1,
    }


def test_student_from_data_resolves_group(group):
    data = {"id": 3, "name": "Иванов П.М.", "group_id": 1}
    student = Student.from_data(data, [group])
    assert student.group is group


def test_student_from_data_unknown_group(group):
    data = {"id": 3, "name": "Иванов П.М.", "group_id": 99}
    with pytest.raises(ValueError):
        Student.from_data(data, [group])


def test_add_student(group):
    students = []
    student = add_student(students, group, "Иванов П.М.")
    assert students == [student]
    assert student.id == 1


def test_add_student_duplicate_forbidden(group):
    students = []
    add_student(students, group, "Иванов П.М.")
    with pytest.raises(ValueError):
        add_student(students, group, "иванов п.м.")


def test_same_name_allowed_in_different_groups(group, other_group):
    students = []
    add_student(students, group, "Иванов П.М.")
    add_student(students, other_group, "Иванов П.М.")
    assert len(students) == 2


def test_group_students_sorted_by_name(group, other_group):
    students = []
    add_student(students, group, "Петров А.И.")
    add_student(students, group, "Абрамов А.С.")
    add_student(students, other_group, "Яковлев Г.Б.")
    names = [s.name for s in get_group_students(students, group)]
    assert names == ["Абрамов А.С.", "Петров А.И."]


def test_find_student(group):
    students = []
    student = add_student(students, group, "Иванов П.М.")
    assert find_student(students, "иван") == [student]
    assert find_student(students, "сидоров") == []
    assert find_student_by_id(students, 1) is student
    assert find_student_by_id(students, 2) is None
