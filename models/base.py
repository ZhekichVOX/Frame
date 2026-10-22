"""Базовый класс сущностей предметной области."""
from abc import ABC, abstractmethod
from typing import Iterable


class Entity(ABC):
    """Сущность с идентификатором, умеющая представить себя в виде данных.

    Базовый класс для Group, Student и Subgroup: общий атрибут id и общий
    контракт to_data() (полиморфизм - каждый класс переопределяет его).
    """

    def __init__(self, entity_id: int) -> None:
        """Создать сущность с заданным идентификатором."""
        self._id = entity_id

    @property
    def id(self) -> int:
        """Идентификатор сущности (только для чтения)."""
        return self._id

    @abstractmethod
    def to_data(self) -> dict:
        """Преобразовать объект в данные для JSON (без ссылок на объекты)."""

    def __repr__(self) -> str:
        """Техническое представление для отладки."""
        return f"{type(self).__name__}(id={self._id})"


def generate_id(entities: Iterable[Entity]) -> int:
    """Вернуть свободный идентификатор для новой сущности."""
    return max((entity.id for entity in entities), default=0) + 1
