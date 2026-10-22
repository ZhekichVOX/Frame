"""Сохранение и загрузка данных проекта в JSON-файлах.

JSON хранит только данные и номера связанных объектов. Преобразование
в объекты и обратно выполняется здесь: при загрузке создаются объекты
Group, Student и Subgroup со ссылками друг на друга, при сохранении
объекты превращаются в словари через to_data().
"""
import json
from pathlib import Path
from typing import Callable, Sequence, TypeVar

from models import Entity, Group, Student, Subgroup

DATA_DIR = Path(__file__).parent / "data"
GROUPS_FILE = DATA_DIR / "groups.json"
STUDENTS_FILE = DATA_DIR / "students.json"
SUBGROUPS_FILE = DATA_DIR / "subgroups.json"

T = TypeVar("T", bound=Entity)


def load_json(filename: Path) -> list[dict]:
    """Загрузить список записей из JSON-файла.

    Если файла нет, возвращается пустой список (первый запуск).

    Raises:
        ValueError: файл повреждён или содержит не список.
    """
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(f"Файл {filename.name} повреждён: {error}") from error
    except OSError as error:
        raise ValueError(
            f"Не удалось прочитать {filename.name}: {error}"
        ) from error
    if not isinstance(data, list):
        raise ValueError(f"Файл {filename.name} должен содержать список")
    return data


def save_json(filename: Path, data: list[dict]) -> None:
    """Сохранить список записей в JSON-файл.

    Raises:
        ValueError: файл не удалось записать.
    """
    try:
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except OSError as error:
        raise ValueError(
            f"Не удалось записать {filename.name}: {error}"
        ) from error


def load_entities(
    filename: Path, factory: Callable[[dict], T]
) -> list[T]:
    """Загрузить файл и создать объекты функцией factory(запись).

    Raises:
        ValueError: файл повреждён или запись не удалось преобразовать.
    """
    entities = []
    for record in load_json(filename):
        try:
            entities.append(factory(record))
        except (KeyError, TypeError) as error:
            raise ValueError(
                f"Некорректная запись в {filename.name}: {error!r}"
            ) from error
    return entities


def save_entities(filename: Path, entities: Sequence[Entity]) -> None:
    """Сохранить объекты в файл; каждый сам отдаёт данные (to_data)."""
    save_json(filename, [entity.to_data() for entity in entities])


def load_groups(filename: Path) -> list[Group]:
    """Загрузить группы из JSON-файла в список объектов Group."""
    return load_entities(filename, Group.from_data)


def save_groups(filename: Path, groups: list[Group]) -> None:
    """Сохранить объекты Group в JSON-файл."""
    save_entities(filename, groups)


def load_students(filename: Path, groups: list[Group]) -> list[Student]:
    """Загрузить студентов, связав каждого с объектом его группы."""
    return load_entities(
        filename, lambda data: Student.from_data(data, groups)
    )


def save_students(filename: Path, students: list[Student]) -> None:
    """Сохранить объекты Student в JSON-файл."""
    save_entities(filename, students)


def load_subgroups(
    filename: Path, groups: list[Group], students: list[Student]
) -> list[Subgroup]:
    """Загрузить подгруппы, восстановив ссылки на группы и студентов."""
    return load_entities(
        filename, lambda data: Subgroup.from_data(data, groups, students)
    )


def save_subgroups(filename: Path, subgroups: list[Subgroup]) -> None:
    """Сохранить объекты Subgroup в JSON-файл."""
    save_entities(filename, subgroups)


def load_all() -> tuple[list[Group], list[Student], list[Subgroup]]:
    """Загрузить группы, студентов и подгруппы со всеми связями.

    Используется консольным и веб-интерфейсом. Файлы читаются заново при
    каждом вызове, поэтому изменения, сделанные в консоли, видны в браузере.

    Raises:
        ValueError: любой из файлов повреждён или содержит неверные данные.
    """
    groups = load_groups(GROUPS_FILE)
    students = load_students(STUDENTS_FILE, groups)
    subgroups = load_subgroups(SUBGROUPS_FILE, groups, students)
    return groups, students, subgroups
