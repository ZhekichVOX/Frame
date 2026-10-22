import pytest

from models import Entity, Group
from models.groups import (
    add_group,
    filter_groups_by_course,
    find_group,
    find_group_by_id,
    require_group,
    show_groups,
    sort_groups,
)


def test_group_creation(group):
    assert group.id == 1
    assert group.name == "ИКБО-01-24"
    assert group.course == 2


def test_group_str_and_repr(group):
    assert str(group) == "ИКБО-01-24 (2 курс)"
    assert repr(group) == "Group(id=1)"


def test_group_is_entity(group):
    assert isinstance(group, Entity)


def test_entity_is_abstract():
    with pytest.raises(TypeError):
        Entity(1)


def test_group_id_is_read_only(group):
    with pytest.raises(AttributeError):
        group.id = 5


def test_group_name_is_stripped_and_validated(group):
    group.name = "  ИКБО-02-24  "
    assert group.name == "ИКБО-02-24"
    with pytest.raises(ValueError):
        group.name = "   "


@pytest.mark.parametrize("course", [0, 7, -1, "2", None])
def test_group_course_validation(group, course):
    with pytest.raises(ValueError):
        group.course = course
    assert group.course == 2


def test_validate_course_static_method():
    assert Group.validate_course(1)
    assert Group.validate_course(6)
    assert not Group.validate_course(7)


def test_group_data_roundtrip(group):
    data = group.to_data()
    assert data == {"id": 1, "name": "ИКБО-01-24", "course": 2}
    restored = Group.from_data(data)
    assert restored.to_data() == data
    assert restored is not group


def test_add_group_returns_object_and_generates_id():
    groups = []
    first = add_group(groups, "ИКБО-01-24", 2)
    second = add_group(groups, "ИВБО-02-23", 3)
    assert (first.id, second.id) == (1, 2)
    assert groups == [first, second]


def test_add_group_duplicate_forbidden():
    groups = []
    add_group(groups, "ИКБО-01-24", 2)
    with pytest.raises(ValueError):
        add_group(groups, "икбо-01-24", 3)
    assert len(groups) == 1


def test_find_group_ignores_case():
    groups = []
    first = add_group(groups, "ИКБО-01-24", 2)
    add_group(groups, "ИВБО-02-23", 3)
    assert find_group(groups, "икбо") == [first]
    assert find_group(groups, "нет такой") == []


def test_require_group(group):
    assert require_group([group], 1) is group
    assert find_group_by_id([group], 9) is None
    with pytest.raises(ValueError):
        require_group([group], 9)


def test_filter_and_sort_groups():
    groups = []
    add_group(groups, "Б-1", 3)
    add_group(groups, "А-1", 2)
    add_group(groups, "В-1", 3)
    assert [g.name for g in filter_groups_by_course(groups, 3)] == [
        "Б-1",
        "В-1",
    ]
    assert [g.name for g in sort_groups(groups)] == ["А-1", "Б-1", "В-1"]


def test_show_groups(capsys, group):
    show_groups([group])
    assert "ИКБО-01-24" in capsys.readouterr().out
    show_groups([])
    assert "Групп пока нет" in capsys.readouterr().out
