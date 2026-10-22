import pytest

from models import Subgroup
from models.subgroups import (
    calc_subgroup_size,
    calc_subgroups_count,
    cancel_subgroups,
    create_subgroups,
    find_student_subgroup,
    get_group_subgroups,
    get_split_status,
    get_student_subgroup,
    get_validation_error,
    is_group_split,
)


def test_calc_subgroups_count():
    assert calc_subgroups_count(25, 12) == 3
    assert calc_subgroups_count(24, 12) == 2
    assert calc_subgroups_count(5, 12) == 1


def test_sizes_are_even_and_sum_to_total():
    sizes = [calc_subgroup_size(25, 3, number) for number in (1, 2, 3)]
    assert sizes == [9, 8, 8]
    assert sum(sizes) == 25


def test_get_student_subgroup():
    assert get_student_subgroup(1, 25, 3) == 1
    assert get_student_subgroup(10, 25, 3) == 2
    assert get_student_subgroup(25, 25, 3) == 3
    assert get_student_subgroup(26, 25, 3) == 0


def test_get_validation_error_and_status():
    assert get_validation_error(10, 5) == ""
    assert get_validation_error(0, 5) != ""
    assert get_validation_error(10, 0) != ""
    assert get_split_status(True) != get_split_status(False)


def test_subgroup_creation(group, make_students):
    members = make_students(group, 3)
    subgroup = Subgroup(1, group, 2, members)
    assert subgroup.group is group
    assert subgroup.number == 2
    assert subgroup.size == 3
    assert subgroup.students == tuple(members)
    assert str(subgroup) == "ИКБО-01-24, подгруппа 2 (3 студ.)"


def test_subgroup_students_is_a_copy(group, make_students):
    subgroup = Subgroup(1, group, 1, make_students(group, 2))
    assert isinstance(subgroup.students, tuple)
    assert subgroup.size == 2


def test_subgroup_rejects_wrong_number(group):
    with pytest.raises(ValueError):
        Subgroup(1, group, 0)


def test_subgroup_rejects_student_of_other_group(
    group, other_group, make_students
):
    stranger = make_students(other_group, 1)[0]
    subgroup = Subgroup(1, group, 1)
    with pytest.raises(ValueError):
        subgroup.add_student(stranger)
    assert subgroup.size == 0


def test_subgroup_rejects_duplicate_student(group, make_students):
    student = make_students(group, 1)[0]
    subgroup = Subgroup(1, group, 1, [student])
    with pytest.raises(ValueError):
        subgroup.add_student(student)
    assert subgroup.has_student(student)


def test_subgroup_data_roundtrip(group, make_students):
    students = make_students(group, 3)
    subgroup = Subgroup(7, group, 2, students[:2])
    data = subgroup.to_data()
    assert data == {
        "id": 7,
        "group_id": 1,
        "number": 2,
        "student_ids": [1, 2],
    }
    restored = Subgroup.from_data(data, [group], students)
    assert restored.group is group
    assert restored.students == tuple(students[:2])


def test_subgroup_from_data_unknown_student(group, make_students):
    data = {"id": 1, "group_id": 1, "number": 1, "student_ids": [99]}
    with pytest.raises(ValueError):
        Subgroup.from_data(data, [group], make_students(group, 3))


def test_create_subgroups_splits_group(group, make_students):
    subgroups = []
    students = make_students(group, 25)
    created = create_subgroups(subgroups, students, group, 12)
    assert [s.size for s in created] == [9, 8, 8]
    assert subgroups == created
    assert is_group_split(subgroups, group)
    assert get_group_subgroups(subgroups, group) == created


def test_create_subgroups_links_objects(group, make_students):
    subgroups = []
    students = make_students(group, 10)
    create_subgroups(subgroups, students, group, 5)
    assert find_student_subgroup(subgroups, students[0]).number == 1
    assert find_student_subgroup(subgroups, students[9]).number == 2


def test_create_subgroups_twice_forbidden(group, make_students):
    subgroups = []
    students = make_students(group, 10)
    create_subgroups(subgroups, students, group, 5)
    with pytest.raises(ValueError):
        create_subgroups(subgroups, students, group, 5)
    assert len(subgroups) == 2


def test_create_subgroups_empty_group(group):
    with pytest.raises(ValueError):
        create_subgroups([], [], group, 5)


def test_other_group_students_are_not_mixed(
    group, other_group, make_students
):
    subgroups = []
    students = make_students(group, 4) + make_students(other_group, 4, 5)
    create_subgroups(subgroups, students, group, 2)
    assert not is_group_split(subgroups, other_group)
    assert all(s.group is group for s in subgroups)


def test_cancelled_subgroups_do_not_block_new_split(group, make_students):
    subgroups = []
    students = make_students(group, 10)
    create_subgroups(subgroups, students, group, 5)
    assert cancel_subgroups(subgroups, group) == 2
    assert subgroups == []
    assert find_student_subgroup(subgroups, students[0]) is None
    recreated = create_subgroups(subgroups, students, group, 4)
    assert len(recreated) == 3
