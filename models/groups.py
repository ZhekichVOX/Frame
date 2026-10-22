"""Класс Group (учебная группа курса) и функции работы с группами."""
from typing import Iterator

from .base import Entity, generate_id


class Group(Entity):
    """Учебная группа определённого курса."""

    MIN_COURSE = 1
    MAX_COURSE = 6

    def __init__(self, group_id: int, name: str, course: int) -> None:
        """Создать группу; название и курс проверяются через сеттеры."""
        super().__init__(group_id)
        self.name = name
        self.course = course

    @staticmethod
    def validate_course(course: int) -> bool:
        """Проверить, что курс - целое число от MIN_COURSE до MAX_COURSE."""
        return (
            isinstance(course, int)
            and Group.MIN_COURSE <= course <= Group.MAX_COURSE
        )

    @property
    def name(self) -> str:
        """Название группы."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Название группы не может быть пустым")
        self._name = value.strip()

    @property
    def course(self) -> int:
        """Номер курса."""
        return self._course

    @course.setter
    def course(self, value: int) -> None:
        if not Group.validate_course(value):
            raise ValueError(
                f"Курс должен быть от {Group.MIN_COURSE} "
                f"до {Group.MAX_COURSE}"
            )
        self._course = value

    @property
    def course_title(self) -> str:
        """Курс в текстовом виде, например '2 курс'."""
        return f"{self._course} курс"

    def to_data(self) -> dict:
        """Данные группы для JSON."""
        return {"id": self.id, "name": self.name, "course": self.course}

    @classmethod
    def from_data(cls, data: dict) -> "Group":
        """Создать группу из данных JSON."""
        return cls(data["id"], data["name"], data["course"])

    def __str__(self) -> str:
        return f"{self.name} ({self.course_title})"


def find_group_by_id(groups: list[Group], group_id: int) -> Group | None:
    """Найти группу по номеру; None, если её нет."""
    for group in groups:
        if group.id == group_id:
            return group
    return None


def require_group(groups: list[Group], group_id: int) -> Group:
    """Вернуть группу по номеру или выбросить ValueError."""
    group = find_group_by_id(groups, group_id)
    if group is None:
        raise ValueError(f"Группа с номером {group_id} не найдена")
    return group


def add_group(groups: list[Group], name: str, course: int) -> Group:
    """Создать группу, добавить в коллекцию и вернуть её.

    Raises:
        ValueError: неверные название или курс, группа уже существует.
    """
    group = Group(generate_id(groups), name, course)
    for existing in groups:
        if existing.name.lower() == group.name.lower():
            raise ValueError(f"Группа {group.name} уже существует")
    groups.append(group)
    return group


def find_group(groups: list[Group], query: str) -> list[Group]:
    """Найти группы, в названии которых есть подстрока query."""
    query = query.strip().lower()
    return [group for group in groups if query in group.name.lower()]


def iter_groups_by_course(
    groups: list[Group], course: int
) -> Iterator[Group]:
    """Генератор групп заданного курса."""
    for group in groups:
        if group.course == course:
            yield group


def filter_groups_by_course(groups: list[Group], course: int) -> list[Group]:
    """Отобрать группы заданного курса."""
    return list(iter_groups_by_course(groups, course))


def sort_groups(groups: list[Group]) -> list[Group]:
    """Отсортировать группы по курсу, затем по названию."""
    return sorted(groups, key=lambda group: (group.course, group.name))


def show_groups(groups: list[Group]) -> None:
    """Вывести список групп в виде таблицы."""
    if not groups:
        print("Групп пока нет")
        return
    print(f"{'№':<4}{'Группа':<16}Курс")
    for group in sort_groups(groups):
        print(f"{group.id:<4}{group.name:<16}{group.course}")
