from datetime import date

import pytest

from utils import get_academic_year, handle_errors, input_int, input_text


def test_academic_year():
    assert get_academic_year(date(2026, 9, 1)) == "2026/2027"
    assert get_academic_year(date(2027, 5, 20)) == "2026/2027"


def test_handle_errors_swallows_value_error(capsys):
    @handle_errors
    def failing() -> None:
        raise ValueError("плохо")

    failing()
    assert "Ошибка: плохо" in capsys.readouterr().out


def test_handle_errors_keeps_metadata_and_other_errors():
    @handle_errors
    def action() -> None:
        """Документация действия."""
        raise KeyError("x")

    assert action.__name__ == "action"
    assert action.__doc__ == "Документация действия."
    with pytest.raises(KeyError):
        action()


def test_input_int_repeats_until_valid(monkeypatch, capsys):
    answers = iter(["abc", "0", "11", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert input_int("? ", 1, 10) == 5
    assert capsys.readouterr().out.count("\n") == 3


def test_input_text_repeats_until_not_empty(monkeypatch):
    answers = iter(["   ", "", " текст "])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert input_text("? ") == "текст"
