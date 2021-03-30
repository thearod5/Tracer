"""
This module is responsible for defining an interface for dictionaries containing trace ids as keys,
notable, this required that the values are transposable.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

ObjectType = TypeVar("ObjectType")


class Transposable(Generic[ObjectType], ABC):  # pylint: disable=too-few-public-methods
    """
    Defines an interface for objects that are able to be transposable
    """

    @abstractmethod
    def transpose(self) -> ObjectType:
        """
        Returns the transpose of child class object type
        :return:
        """
