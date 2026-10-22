"""Класс Subgroup и функции формирования учебных подгрупп.

Функции расчёта (get_validation_error, calc_subgroups_count,
calc_subgroup_size, get_student_subgroup) перенесены из ПР1 без изменений
логики: они работают с числами и не относятся к конкретному объекту.
"""
import math
from typing import Iterable

from .base import Entity, generate_id
from .groups import Group, require_group
from .students import Student, find_student_by_id, get_group_students


class Subgroup(Entity):
    """Подгруппа: часть учебной группы с набором студентов.

    Композиция: подгруппа хранит ссылку на Group и на объекты Student.
    """

    def __init__(
        self,
        subgroup_id: int,
        group: Group,
        number: int,
        students: Iterable[Student] = (),
    ) -> None:
        """Создать подгруппу; студенты добавляются через add_student()."""
        super().__init__(subgroup_id)
        if not isinstance(number, int) or number < 1:
            raise ValueError("Номер подгруппы должен быть не меньше 1")
        self._group = group
        self._number = number
        self._students: list[Student] = []
        for student in students:
            self.add_student(student)

    @property
    def group(self) -> Group:
        """Группа, к которой относится подгруппа."""
        return self._group

    @property
    def number(self) -> int:
        """Номер подгруппы внутри группы."""
        return self._number

    @property
    def students(self) -> tuple[Student, ...]:
        """Студенты подгруппы (копия: состав меняется только методами)."""
        return tuple(self._students)

    @property
    def size(self) -> int:
        """Число студентов в подгруппе."""
        return len(self._students)

    def add_student(self, student: Student) -> None:
        """Добавить студента в подгруппу.

        Raises:
            ValueError: студент из другой группы или уже в подгруппе.
        """
        if not student.belongs_to(self._group):
            raise ValueError(
                f"{student.name} не учится в группе {self._group.name}"
            )
        if self.has_student(student):
            raise ValueError(f"{student.name} уже в этой подгруппе")
        self._students.append(student)

    def has_student(self, student: Student) -> bool:
        """Проверить, входит ли студент в подгруппу."""
        return student in self._students

    def to_data(self) -> dict:
        """Данные подгруппы для JSON: вместо объектов - их номера."""
        return {
            "id": self.id,
            "group_id": self.group.id,
            "number": self.number,
            "student_ids": [student.id for student in self._students],
        }

    @classmethod
    def from_data(
        cls,
        data: dict,
        groups: list[Group],
        students: list[Student],
    ) -> "Subgroup":
        """Создать подгруппу из данных JSON, восстановив связи.

        Raises:
            ValueError: группа или студент с указанным номером не найдены.
        """
        group = require_group(groups, data["group_id"])
        members = []
        for student_id in data["student_ids"]:
            student = find_student_by_id(students, student_id)
            if student is None:
                raise ValueError(f"Студент с номером {student_id} не найден")
            members.append(student)
        return cls(data["id"], group, data["number"], members)

    def __str__(self) -> str:
        return (
            f"{self.group.name}, подгруппа {self.number} "
            f"({self.size} студ.)"
        )


def get_validation_error(students_count: int, max_subgroup_size: int) -> str:
    """Проверить параметры; вернуть текст ошибки или пустую строку."""
    if students_count < 1:
        return "В группе должен быть хотя бы один студент"
    if max_subgroup_size < 1:
        return "Максимальный размер подгруппы должен быть не меньше 1"
    return ""


def calc_subgroups_count(students_count: int, max_subgroup_size: int) -> int:
    """Минимальное число подгрупп, при котором ни одна не превышает лимит."""
    return math.ceil(students_count / max_subgroup_size)


def calc_subgroup_size(
    students_count: int, subgroups_count: int, subgroup_number: int
) -> int:
    """Размер подгруппы с заданным номером при равномерном распределении.

    Остаток студентов добавляется по одному в первые подгруппы.
    """
    base_size = students_count // subgroups_count
    extra_students = students_count % subgroups_count
    if subgroup_number <= extra_students:
        return base_size + 1
    return base_size


def get_student_subgroup(
    student_number: int, students_count: int, subgroups_count: int
) -> int:
    """Номер подгруппы студента по его номеру в списке группы.

    Студенты распределяются последовательно: сначала заполняются
    более крупные подгруппы, затем остальные.
    Если номер вне диапазона 1..students_count, возвращается 0.
    """
    if student_number < 1 or student_number > students_count:
        return 0
    base_size = students_count // subgroups_count
    extra_students = students_count % subgroups_count
    big_size = base_size + 1
    big_border = extra_students * big_size
    if student_number <= big_border:
        return (student_number - 1) // big_size + 1
    return extra_students + (student_number - big_border - 1) // base_size + 1


def get_split_status(is_split: bool) -> str:
    """Вернуть текстовый статус группы."""
    if is_split:
        return "Группа уже разделена на подгруппы"
    return "Группа ещё не разделена на подгруппы"


def find_subgroup_by_id(
    subgroups: list[Subgroup], subgroup_id: int
) -> Subgroup | None:
    """Найти подгруппу по номеру; None, если её нет."""
    for subgroup in subgroups:
        if subgroup.id == subgroup_id:
            return subgroup
    return None


def get_group_subgroups(
    subgroups: list[Subgroup], group: Group
) -> list[Subgroup]:
    """Подгруппы заданной группы в порядке номеров."""
    selected = [s for s in subgroups if s.group is group]
    return sorted(selected, key=lambda subgroup: subgroup.number)


def is_group_split(subgroups: list[Subgroup], group: Group) -> bool:
    """Проверить, сформированы ли подгруппы для группы."""
    return any(subgroup.group is group for subgroup in subgroups)


def create_subgroups(
    subgroups: list[Subgroup],
    students: list[Student],
    group: Group,
    max_subgroup_size: int,
) -> list[Subgroup]:
    """Разделить группу на подгруппы и добавить их в коллекцию subgroups.

    Returns:
        Список созданных подгрупп.

    Raises:
        ValueError: неверные параметры или группа уже разделена.
    """
    group_students = get_group_students(students, group)
    students_count = len(group_students)
    error = get_validation_error(students_count, max_subgroup_size)
    if error:
        raise ValueError(error)
    if is_group_split(subgroups, group):
        raise ValueError("Подгруппы группы уже сформированы")

    subgroups_count = calc_subgroups_count(students_count, max_subgroup_size)
    created = []
    for number in range(1, subgroups_count + 1):
        subgroup = Subgroup(generate_id(subgroups), group, number)
        subgroups.append(subgroup)
        created.append(subgroup)
    for position, student in enumerate(group_students, start=1):
        number = get_student_subgroup(
            position, students_count, subgroups_count
        )
        created[number - 1].add_student(student)
    return created


def cancel_subgroups(subgroups: list[Subgroup], group: Group) -> int:
    """Расформировать подгруппы группы; вернуть число удалённых."""
    remaining = [s for s in subgroups if s.group is not group]
    removed = len(subgroups) - len(remaining)
    subgroups[:] = remaining
    return removed


def find_student_subgroup(
    subgroups: list[Subgroup], student: Student
) -> Subgroup | None:
    """Найти подгруппу студента; None, если студент не распределён."""
    for subgroup in subgroups:
        if subgroup.has_student(student):
            return subgroup
    return None


def show_subgroups(subgroups: list[Subgroup]) -> None:
    """Вывести подгруппы с составом студентов."""
    for subgroup in subgroups:
        print(f"\n{subgroup}:")
        for student in subgroup.students:
            print(f"  - {student.name}")
