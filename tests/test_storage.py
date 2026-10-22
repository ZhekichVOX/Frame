import pytest

from models.students import add_student
from models.subgroups import create_subgroups
from storage import (
    load_groups,
    load_json,
    load_students,
    load_subgroups,
    save_groups,
    save_json,
    save_students,
    save_subgroups,
)


def test_object_graph_roundtrip(tmp_path, group, make_students):
    students = make_students(group, 10)
    subgroups = []
    create_subgroups(subgroups, students, group, 5)

    save_groups(tmp_path / "g.json", [group])
    save_students(tmp_path / "s.json", students)
    save_subgroups(tmp_path / "sg.json", subgroups)

    groups2 = load_groups(tmp_path / "g.json")
    students2 = load_students(tmp_path / "s.json", groups2)
    subgroups2 = load_subgroups(tmp_path / "sg.json", groups2, students2)

    assert [g.to_data() for g in groups2] == [group.to_data()]
    assert [s.to_data() for s in students2] == [s.to_data() for s in students]
    assert [s.to_data() for s in subgroups2] == [
        s.to_data() for s in subgroups
    ]


def test_loaded_objects_are_linked_by_reference(
    tmp_path, group, make_students
):
    students = make_students(group, 4)
    subgroups = []
    create_subgroups(subgroups, students, group, 2)
    save_groups(tmp_path / "g.json", [group])
    save_students(tmp_path / "s.json", students)
    save_subgroups(tmp_path / "sg.json", subgroups)

    groups2 = load_groups(tmp_path / "g.json")
    students2 = load_students(tmp_path / "s.json", groups2)
    subgroups2 = load_subgroups(tmp_path / "sg.json", groups2, students2)

    assert all(s.group is groups2[0] for s in students2)
    assert subgroups2[0].group is groups2[0]
    assert subgroups2[0].students[0] is students2[0]


def test_json_has_ids_not_objects(tmp_path, group):
    students = []
    add_student(students, group, "Иванов П.М.")
    save_students(tmp_path / "s.json", students)
    assert load_json(tmp_path / "s.json") == [
        {"id": 1, "name": "Иванов П.М.", "group_id": 1}
    ]


def test_load_student_with_unknown_group_raises(tmp_path, group):
    save_json(tmp_path / "s.json", [{"id": 1, "name": "А", "group_id": 9}])
    with pytest.raises(ValueError):
        load_students(tmp_path / "s.json", [group])


def test_load_record_without_field_raises(tmp_path):
    save_json(tmp_path / "g.json", [{"id": 1, "name": "ИКБО-01-24"}])
    with pytest.raises(ValueError):
        load_groups(tmp_path / "g.json")


def test_load_record_with_invalid_value_raises(tmp_path):
    save_json(
        tmp_path / "g.json", [{"id": 1, "name": "ИКБО-01-24", "course": 9}]
    )
    with pytest.raises(ValueError):
        load_groups(tmp_path / "g.json")


def test_load_missing_file_returns_empty(tmp_path):
    assert load_json(tmp_path / "missing.json") == []
    assert load_groups(tmp_path / "missing.json") == []


def test_load_broken_json_raises(tmp_path):
    filename = tmp_path / "broken.json"
    filename.write_text("{не json", encoding="utf-8")
    with pytest.raises(ValueError):
        load_json(filename)


def test_load_not_a_list_raises(tmp_path):
    filename = tmp_path / "dict.json"
    filename.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        load_json(filename)


def test_save_json_keeps_cyrillic_and_creates_dir(tmp_path):
    filename = tmp_path / "data" / "students.json"
    save_json(filename, [{"name": "Иванов"}])
    assert "Иванов" in filename.read_text(encoding="utf-8")
