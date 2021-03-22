"""
TODO
"""
import inspect
from abc import abstractmethod, ABC
from enum import Enum
from typing import Type, TypeVar

from api.constants.techniques import (
    ArtifactPathType,
    LEVELS_DELIMITER,
    TECHNIQUE_DELIMITER,
    UNDEFINED_TECHNIQUE,
)
from api.experiment.file_operations import list_to_string


class ITechniqueDefinition(ABC):
    """
    TODO
    """

    def __init__(self, parameters: [str], components: [str], is_stochastic=False):
        self.parameters = parameters
        self.components = components
        self._component_techniques = (
            []
        )  # untyped to avoid circular imports but TODO should be ITechnique
        self._is_stochastic = is_stochastic
        self.source_level = -1
        self.target_level = -1
        self.parse()
        self.validate()
        assert self.source_level != -1 and self.target_level != -1

    @abstractmethod
    def parse(self):
        """
        TODO
        :return:
        """

    @abstractmethod
    def validate(self):
        """
        TODO
        :return:
        """

    @staticmethod
    @abstractmethod
    def get_symbol() -> str:
        """
        TODO
        :return:
        """

    def get_name(self) -> str:
        """
        TODO
        :return:
        """
        return "(%s %s %s)" % (
            self.get_symbol(),
            list_to_string(self.parameters),
            list_to_string(self.components),
        )

    def get_attributes(self) -> [str]:
        """
        TODO
        :return:
        """
        return get_public_variables(ITechniqueDefinition) + get_public_variables(
            self.__class__
        )

    def to_dict(self):
        """
        TODO
        :return:
        """
        property_names = self.get_attributes()
        property_values = self.get_properties_as_strings()
        return dict(zip(property_names, property_values))

    def get_properties_as_strings(self) -> [str]:
        """
        TODO
        :return:
        """
        property_names = self.get_attributes()
        property_values = [getattr(self, prop) for prop in property_names]
        str_components = []

        for property_value in property_values:
            if isinstance(property_value, str):
                str_components.append(property_value)
            elif isinstance(property_value, list):
                str_components.append(stringify_paths(property_value))
            elif property_value is None:
                str_components.append(UNDEFINED_TECHNIQUE)
            elif isinstance(property_value, Enum):
                str_components.append(property_value.value)
        return str_components

    def contains_stochastic_technique(self):
        """
        TODO
        :return:
        """
        return self._is_stochastic or any(
            map(
                lambda t: t.definition.contains_stochastic_technique(),
                self._component_techniques,
            )
        )


def stringify_paths(artifact_paths: ArtifactPathType) -> str:
    """
    TODO
    :param artifact_paths:
    :return:
    """
    levels_str = []
    for levels_in_technique in artifact_paths:
        levels_in_technique_str = list(map(str, levels_in_technique))
        levels_str.append(LEVELS_DELIMITER.join(levels_in_technique_str))
    return TECHNIQUE_DELIMITER.join(levels_str)


def get_public_variables(some_class: object):
    """
    TODO
    :param some_class:
    :return:
    """
    public_properties = get_public_fields(some_class)
    public_attributes = [
        key
        for key in public_properties
        if not inspect.isroutine(getattr(some_class, key))
    ]
    return public_attributes


def get_public_fields(some_class: object):
    """
    TODO
    :param some_class:
    :return:
    """
    return [key for key, _ in vars(some_class).items() if key[0] != "_"]


GenericClass = TypeVar("GenericClass")


def get_missing_attributes(
    source: ITechniqueDefinition, target_class: Type[GenericClass]
) -> [str]:
    """
    TODO
    :param source:
    :param target_class:
    :return:
    """
    source_attributes = source.get_attributes()
    return [
        target_class_attribute
        for target_class_attribute in get_public_variables(target_class)
        if target_class_attribute not in source_attributes
    ]
