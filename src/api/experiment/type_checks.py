"""
Contains list of type-casting functions.
"""
from typing import Optional


def to_string(opt_str: Optional[str]) -> str:
    """
    Type-casts given optional string into a string if it is not in fact None
    :param opt_str: either none or a string
    :return: string
    :raises:
        ValueError: If given opt_str is None
    """
    if opt_str is None:
        raise ValueError("Expected string received None")
    new_str: str = opt_str
    return new_str


def to_int(opt_int: Optional[int]) -> int:
    """
    Type-casts given optional int into a int if it is not in fact None
    :param opt_int: either none or a int
    :return: int
    :raises:
        ValueError: If given opt_str is None
    """
    if opt_int is None:
        raise ValueError("Expected int received None")
    new_str: int = opt_int
    return new_str
