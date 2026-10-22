"""Сервис формирования учебных подгрупп: точка запуска и меню."""
from datetime import date

from models import Group, Student, Subgroup
from models.groups import (
    add_group,
    filter_groups_by_course,
    find_group,
    require_group,
    show_groups,
)
from models.students import (
    add_student,
    find_student,
    get_group_students,
    show_students,
)
from models.subgroups import (
    calc_subgroup_size,
    calc_subgroups_count,
    cancel_subgroups,
    create_subgroups,
    find_student_subgroup,
    get_group_subgroups,
    get_split_status,
    get_validation_error,
    is_group_split,
    show_subgroups,
)
from storage import (
    GROUPS_FILE,
    STUDENTS_FILE,
    SUBGROUPS_FILE,
    load_all,
    save_groups,
    save_students,
    save_subgroups,
)
from utils import get_academic_year, handle_errors, input_int, input_text

MENU = """
1. Показать группы
2. Добавить группу
3. Найти группу по названию
4. Показать группы курса
5. Показать студентов группы
6. Добавить студента в группу
7. Рассчитать разбиение на подгруппы
8. Сформировать подгруппы
9. Показать подгруппы группы
10. Найти подгруппу студента
11. Расформировать подгруппы
0. Выход"""

CHANGING_ACTIONS = {"2", "6", "8", "11"}


def ask_group(groups: list[Group]) -> Group:
    """Показать группы и запросить номер существующей группы."""
    show_groups(groups)
    return require_group(groups, input_int("Номер группы: "))


@handle_errors
def action_add_group(groups: list[Group]) -> None:
    """Пункт меню: добавить группу."""
    name = input_text("Название группы: ")
    course = input_int(
        f"Курс ({Group.MIN_COURSE}-{Group.MAX_COURSE}): ",
        Group.MIN_COURSE,
        Group.MAX_COURSE,
    )
    group = add_group(groups, name, course)
    print(f"Добавлена группа: {group} под номером {group.id}")


@handle_errors
def action_find_group(groups: list[Group]) -> None:
    """Пункт меню: поиск группы по подстроке названия."""
    found = find_group(groups, input_text("Часть названия: "))
    if found:
        show_groups(found)
    else:
        print("Ничего не найдено")


@handle_errors
def action_filter_groups(groups: list[Group]) -> None:
    """Пункт меню: показать группы выбранного курса."""
    course = input_int("Курс: ", Group.MIN_COURSE, Group.MAX_COURSE)
    selected = filter_groups_by_course(groups, course)
    if selected:
        show_groups(selected)
    else:
        print(f"На курсе {course} групп нет")


@handle_errors
def action_show_students(
    groups: list[Group], students: list[Student]
) -> None:
    """Пункт меню: показать студентов группы."""
    group = ask_group(groups)
    show_students(get_group_students(students, group))


@handle_errors
def action_add_student(
    groups: list[Group],
    students: list[Student],
    subgroups: list[Subgroup],
) -> None:
    """Пункт меню: добавить студента; подгруппы группы расформировываются."""
    group = ask_group(groups)
    student = add_student(students, group, input_text("ФИО студента: "))
    print(f"Добавлен студент: {student}")
    if cancel_subgroups(subgroups, group):
        print("Состав группы изменился: подгруппы нужно сформировать заново")


@handle_errors
def action_plan(groups: list[Group], students: list[Student]) -> None:
    """Пункт меню: рассчитать разбиение на подгруппы (сценарий ПР1)."""
    group = ask_group(groups)
    students_count = len(get_group_students(students, group))
    max_size = input_int("Максимум студентов в подгруппе: ")
    error = get_validation_error(students_count, max_size)
    if error:
        print(f"Ошибка: {error}")
        return

    subgroups_count = calc_subgroups_count(students_count, max_size)
    print(f"\n{group}: {students_count} студ.")
    if subgroups_count == 1:
        print("Деление на подгруппы не требуется")
        return
    print(f"Нужно подгрупп: {subgroups_count}")
    for number in range(1, subgroups_count + 1):
        size = calc_subgroup_size(students_count, subgroups_count, number)
        print(f"  Подгруппа {number}: {size} студ.")


@handle_errors
def action_create_subgroups(
    groups: list[Group],
    students: list[Student],
    subgroups: list[Subgroup],
) -> None:
    """Пункт меню: сформировать подгруппы группы."""
    group = ask_group(groups)
    print(get_split_status(is_group_split(subgroups, group)))
    max_size = input_int("Максимум студентов в подгруппе: ")
    created = create_subgroups(subgroups, students, group, max_size)
    print(f"Сформировано подгрупп: {len(created)}")
    show_subgroups(created)


@handle_errors
def action_show_subgroups(
    groups: list[Group], subgroups: list[Subgroup]
) -> None:
    """Пункт меню: показать подгруппы группы."""
    group = ask_group(groups)
    selected = get_group_subgroups(subgroups, group)
    if selected:
        show_subgroups(selected)
    else:
        print(get_split_status(False))


@handle_errors
def action_student_subgroup(
    students: list[Student], subgroups: list[Subgroup]
) -> None:
    """Пункт меню: определить подгруппу студента по части ФИО."""
    found = find_student(students, input_text("Часть ФИО: "))
    if not found:
        print("Студент не найден")
        return
    for student in found:
        subgroup = find_student_subgroup(subgroups, student)
        if subgroup is None:
            result = "подгруппы нет"
        else:
            result = f"подгруппа {subgroup.number}"
        print(f"{student}: {result}")


@handle_errors
def action_cancel_subgroups(
    groups: list[Group], subgroups: list[Subgroup]
) -> None:
    """Пункт меню: расформировать подгруппы группы."""
    group = ask_group(groups)
    print(f"Расформировано подгрупп: {cancel_subgroups(subgroups, group)}")


def save_all(
    groups: list[Group],
    students: list[Student],
    subgroups: list[Subgroup],
) -> None:
    """Сохранить все данные проекта в JSON-файлы."""
    save_groups(GROUPS_FILE, groups)
    save_students(STUDENTS_FILE, students)
    save_subgroups(SUBGROUPS_FILE, subgroups)


def run_action(
    choice: str,
    groups: list[Group],
    students: list[Student],
    subgroups: list[Subgroup],
) -> bool:
    """Выполнить пункт меню; вернуть False, если выбран неверный пункт."""
    if choice == "1":
        show_groups(groups)
    elif choice == "2":
        action_add_group(groups)
    elif choice == "3":
        action_find_group(groups)
    elif choice == "4":
        action_filter_groups(groups)
    elif choice == "5":
        action_show_students(groups, students)
    elif choice == "6":
        action_add_student(groups, students, subgroups)
    elif choice == "7":
        action_plan(groups, students)
    elif choice == "8":
        action_create_subgroups(groups, students, subgroups)
    elif choice == "9":
        action_show_subgroups(groups, subgroups)
    elif choice == "10":
        action_student_subgroup(students, subgroups)
    elif choice == "11":
        action_cancel_subgroups(groups, subgroups)
    else:
        return False
    return True


def main() -> None:
    """Точка запуска: загрузка объектов и цикл меню."""
    try:
        groups, students, subgroups = load_all()
    except ValueError as error:
        print(f"Ошибка загрузки данных: {error}")
        return

    print("=== Формирование учебных подгрупп ===")
    print(f"Учебный год: {get_academic_year(date.today())}")
    while True:
        print(MENU)
        try:
            choice = input("\nВыберите действие: ").strip()
            if choice == "0":
                break
            if not run_action(choice, groups, students, subgroups):
                print("Нет такого пункта меню")
            elif choice in CHANGING_ACTIONS:
                save_all(groups, students, subgroups)
        except ValueError as error:
            print(f"Ошибка сохранения: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nВвод прерван")
            break
    print("До свидания!")


if __name__ == "__main__":
    main()
