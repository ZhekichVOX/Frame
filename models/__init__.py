"""Объектная модель предметной области: группы, студенты, подгруппы."""
from .base import Entity
from .groups import Group
from .students import Student
from .subgroups import Subgroup

__all__ = ["Entity", "Group", "Student", "Subgroup"]
