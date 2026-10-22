import re
from pathlib import Path

import pytest
from django.contrib.staticfiles import finders
from django.template.loader import get_template
from django.test import override_settings
from django.urls import resolve, reverse

import groups.views
import homepage.views
import students.views
import subgroups.views
from models import Group, Student
from storage import save_groups, save_students, save_subgroups

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    "/",
    "/groups/",
    "/groups/1/",
    "/students/",
    "/students/1/",
    "/subgroups/",
    "/subgroups/1/",
]


def get(client, url):
    response = client.get(url)
    return response, response.content.decode()


def template_names(response):
    return [template.name for template in response.templates]


# --- маршруты и пространства имён ---------------------------------------


@pytest.mark.parametrize(
    "name, path",
    [
        ("homepage:index", "/"),
        ("groups:list", "/groups/"),
        ("students:list", "/students/"),
        ("subgroups:list", "/subgroups/"),
    ],
)
def test_namespaced_url_names_resolve_to_paths(name, path):
    assert reverse(name) == path


@pytest.mark.parametrize(
    "name, args, path",
    [
        ("groups:detail", [3], "/groups/3/"),
        ("students:detail", [7], "/students/7/"),
        ("subgroups:detail", [2], "/subgroups/2/"),
    ],
)
def test_detail_urls_are_built_from_id(name, args, path):
    assert reverse(name, args=args) == path


def test_dynamic_url_is_routed_with_namespace_and_int_parameter():
    match = resolve("/groups/1/")
    assert match.func is groups.views.group_detail
    assert match.namespace == "groups"
    assert match.url_name == "detail"
    assert match.kwargs == {"group_id": 1}


def test_non_integer_id_does_not_match_route(client):
    assert client.get("/groups/abc/").status_code == 404


# --- страницы: шаблоны, контекст, статика -------------------------------


@pytest.mark.parametrize("url", PAGES)
def test_pages_render_through_base_template(client, url):
    response, html = get(client, url)
    assert response.status_code == 200
    names = template_names(response)
    assert "base.html" in names
    assert "includes/navigation.html" in names
    assert 'name="viewport"' in html
    assert "bootstrap" in html
    assert "homepage/css/style.css" in html
    assert "homepage/js/main.js" in html
    assert "homepage/img/logo.svg" in html


@pytest.mark.parametrize(
    "url, template",
    [
        ("/", "homepage/index.html"),
        ("/groups/", "groups/group_list.html"),
        ("/groups/1/", "groups/group_detail.html"),
        ("/students/", "students/student_list.html"),
        ("/students/1/", "students/student_detail.html"),
        ("/subgroups/", "subgroups/subgroup_list.html"),
        ("/subgroups/1/", "subgroups/subgroup_detail.html"),
    ],
)
def test_each_page_uses_its_template(client, url, template):
    response, _ = get(client, url)
    assert template in template_names(response)


def test_index_context_and_filters(client):
    response, html = get(client, "/")
    assert len(response.context["groups"]) == 2
    assert len(response.context["students"]) == 5
    assert len(response.context["subgroups"]) == 2
    assert "Формирование учебных подгрупп" in html
    assert re.search(
        r"Учебный год \d{4}/\d{4} · сегодня \d\d\.\d\d\.\d{4}", html
    )
    assert 'href="/groups/"' in html


def test_group_list_context_include_and_filters(client):
    response, html = get(client, "/groups/")
    items = response.context["items"]
    names = [item["group"].name for item in items]
    assert names == ["ИКБО-01-24", "ИВБО-02-23"]
    assert items[0]["students_count"] == 5 and items[0]["is_split"]
    assert not items[1]["is_split"]
    assert "groups/includes/group_card.html" in template_names(response)
    assert "subgroups/includes/split_status.html" in template_names(response)
    assert "Всего групп: 2" in html
    assert "разделена" in html and "не разделена" in html
    assert 'href="/groups/1/"' in html


def test_group_detail_context(client):
    response, html = get(client, "/groups/1/")
    assert response.context["group"].name == "ИКБО-01-24"
    assert len(response.context["students"]) == 5
    assert [s.number for s in response.context["subgroups"]] == [1, 2]
    assert response.context["is_split"] is True
    assert "Студент 01" in html and "Студент 05" in html
    assert 'href="/subgroups/1/"' in html
    assert 'href="/students/1/"' in html


def test_group_without_subgroups(client):
    response, html = get(client, "/groups/2/")
    assert response.context["is_split"] is False
    assert "Студентов нет." in html
    assert "<h2 class=\"h4\">Подгруппы</h2>" not in html


def test_student_pages(client):
    _, html = get(client, "/students/")
    assert "Всего студентов: 5" in html
    assert "students/includes/student_row.html" in template_names(
        client.get("/students/")
    )
    response, html = get(client, "/students/1/")
    assert response.context["subgroup"].number == 1
    assert 'href="/groups/1/"' in html
    assert "подгруппа 1" in html


def test_student_list_is_grouped_and_numbered_sequentially(
    client, web_data, other_group
):
    students = [
        *web_data["students"],
        Student(6, "Яковлев Г.Б.", other_group),
        Student(7, "Андреев О.К.", other_group),
    ]
    save_students(web_data["files"]["STUDENTS_FILE"], students)
    response, html = get(client, "/students/")
    items = response.context["items"]
    # сначала группа 2 курса (ИКБО), затем 3 курса (ИВБО); внутри - по ФИО
    assert [i["student"].id for i in items] == [1, 2, 3, 4, 5, 7, 6]
    numbers = re.findall(r"<tr>\s*<td>(\d+)</td>", html)
    assert numbers == ["1", "2", "3", "4", "5", "6", "7"]


def test_subgroup_pages(client):
    response, html = get(client, "/subgroups/")
    assert "Всего подгрупп: 2" in html
    assert "ИКБО-01-24, подгруппа 1 (3 студ.)" in html
    assert "subgroups/includes/subgroup_card.html" in template_names(response)
    _, html = get(client, "/subgroups/2/")
    assert "Студент 04" in html and "Студент 05" in html
    assert "Студент 01" not in html


# --- пустые коллекции ---------------------------------------------------


def test_empty_collections_show_hints(client, web_data):
    files = web_data["files"]
    save_subgroups(files["SUBGROUPS_FILE"], [])
    save_students(files["STUDENTS_FILE"], [])
    save_groups(files["GROUPS_FILE"], [])
    for url, hint in [
        ("/groups/", "Групп пока нет."),
        ("/students/", "Студентов пока нет."),
        ("/subgroups/", "ещё не сформированы"),
    ]:
        response, html = get(client, url)
        assert response.status_code == 200
        assert hint in html


# --- 404 ----------------------------------------------------------------


@pytest.mark.parametrize(
    "url, message",
    [
        ("/groups/999/", "Группа не найдена"),
        ("/students/999/", "Студент не найден"),
        ("/subgroups/999/", "Подгруппа не найдена"),
    ],
)
def test_missing_object_returns_404_from_template(client, url, message):
    response, html = get(client, url)
    assert response.status_code == 404
    assert message in html
    assert "base.html" in template_names(response)


@override_settings(DEBUG=False)
def test_custom_404_handler_uses_template(client):
    response, html = get(client, "/nonexistent/")
    assert response.status_code == 404
    assert "404.html" in template_names(response)
    assert "404 – страница не найдена" in html
    assert 'href="/"' in html


# --- безопасность и навигация -------------------------------------------


def test_user_data_is_autoescaped(client, web_data, other_group):
    evil = Group(3, "<b>XSS</b>", 1)
    groups_list = [web_data["group"], other_group, evil]
    save_groups(web_data["files"]["GROUPS_FILE"], groups_list)
    for url in ("/groups/", "/groups/3/"):
        _, html = get(client, url)
        assert "<b>XSS</b>" not in html
        assert "&lt;b&gt;XSS&lt;/b&gt;" in html


@pytest.mark.parametrize(
    "url, active",
    [
        ("/", "Главная"),
        ("/groups/1/", "Группы"),
        ("/students/", "Студенты"),
        ("/subgroups/2/", "Подгруппы"),
    ],
)
def test_navigation_highlights_current_section(client, url, active):
    _, html = get(client, url)
    active_links = re.findall(r'class="nav-link active"[^>]*>([^<]+)<', html)
    assert active_links == [active]


# --- архитектура: шаблоны вместо HTML в Python ---------------------------


def test_page_helper_is_gone():
    assert not hasattr(homepage.views, "page")
    assert not hasattr(homepage.views, "not_found")


@pytest.mark.parametrize(
    "module", [homepage.views, groups.views, students.views, subgroups.views]
)
def test_views_do_not_build_html(module):
    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "HttpResponse(" not in source
    assert "<div" not in source and "<a href" not in source
    assert "render(" in source


def all_templates():
    found = [
        *(ROOT / "templates").rglob("*.html"),
        *ROOT.glob("*/templates/**/*.html"),
    ]
    return sorted(set(found))


def test_templates_exist_in_expected_places():
    names = {path.name for path in all_templates()}
    assert {
        "base.html",
        "navigation.html",
        "404.html",
        "index.html",
        "group_list.html",
        "group_detail.html",
        "group_card.html",
        "split_status.html",
    } <= names


@pytest.mark.parametrize("path", all_templates(), ids=lambda p: p.name)
def test_template_compiles_and_has_no_hardcoded_links(path):
    text = path.read_text(encoding="utf-8")
    assert not re.search(r'href="/', text), "используйте {% url %}"
    assert text.count("{% if") == text.count("{% endif %}")
    assert text.count("{% for") == text.count("{% endfor %}")
    relative = path.as_posix().split("/templates/", 1)[1]
    get_template(relative)


def test_static_files_are_found():
    for name in (
        "homepage/css/style.css",
        "homepage/js/main.js",
        "homepage/img/logo.svg",
    ):
        assert finders.find(name), name
