"""Класс Student и функции работы со студентами."""
from typing import Iterator

from .base import Entity, generate_id
from .groups import Group, require_group


class Student(Entity):
    """Студент, входящий в одну учебную группу."""

    def __init__(self, student_id: int, name: str, group: Group) -> None:
        """Создать студента; хранится ссылка на объект группы."""
        super().__init__(student_id)
        self.name = name
        self._group = group

    @property
    def name(self) -> str:
        """ФИО студента."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ФИО студента не может быть пустым")
        self._name = value.strip()

    @property
    def group(self) -> Group:
        """Группа студента (только для чтения)."""
        return self._group

    def belongs_to(self, group: Group) -> bool:
        """Проверить, что студент входит в указанную группу."""
        return self._group is group

    def to_data(self) -> dict:
        """Данные студента для JSON: вместо группы - её номер."""
        return {
            "id": self.id,
            "name": self.name,
            "group_id": self.group.id,
        }

    @classmethod
    def from_data(cls, data: dict, groups: list[Group]) -> "Student":
        """Создать студента из данных JSON, найдя его группу в groups."""
        group = require_group(groups, data["group_id"])
        return cls(data["id"], data["name"], group)

    def __str__(self) -> str:
        return f"{self.name} ({self.group.name})"


def find_student_by_id(
    students: list[Student], student_id: int
) -> Student | None:
    """Найти студента по номеру; None, если его нет."""
    for student in students:
        if student.id == student_id:
            return student
    return None


def add_student(
    students: list[Student], group: Group, name: str
) -> Student:
    """Создать студента в группе, добавить в коллекцию и вернуть его.

    Raises:
        ValueError: пустое ФИО или такой студент уже есть в группе.
    """
    student = Student(generate_id(students), name, group)
    for existing in iter_group_students(students, group):
        if existing.name.lower() == student.name.lower():
            raise ValueError(f"Студент {student.name} уже есть в группе")
    students.append(student)
    return student


def iter_group_students(
    students: list[Student], group: Group
) -> Iterator[Student]:
    """Генератор студентов заданной группы в порядке хранения."""
    for student in students:
        if student.belongs_to(group):
            yield student


def get_group_students(
    students: list[Student], group: Group
) -> list[Student]:
    """Студенты группы в алфавитном порядке (порядок списка группы)."""
    return sorted(
        iter_group_students(students, group),
        key=lambda student: student.name,
    )


def find_student(students: list[Student], query: str) -> list[Student]:
    """Найти студентов, в ФИО которых есть подстрока query."""
    query = query.strip().lower()
    return [s for s in students if query in s.name.lower()]


def show_students(students: list[Student]) -> None:
    """Вывести пронумерованный список студентов."""
    if not students:
        print("Студентов в группе нет")
        return
    for number, student in enumerate(students, start=1):
        print(f"{number:>3}. {student.name}")
