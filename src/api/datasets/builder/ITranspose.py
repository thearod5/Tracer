"""
This module is responsible for defining an interface for dictionaries containing trace ids as keys,
notable, this required that the values are transposable.
"""
from typing import Generic, TypeVar

ObjectType = TypeVar("ObjectType")


class Transposable(Generic[ObjectType]):
    """
    Defines an interface for objects that are able to be transposable
    """

    def transpose(self) -> ObjectType:
        pass
