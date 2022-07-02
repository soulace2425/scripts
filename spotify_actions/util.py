"""
util.py
02 July 2022 01:13:57

Utility functions.
"""

from typing import Any, Callable, Optional, Sequence


def find(predicate: Callable[[Any], bool], sequence: Sequence) -> Optional[Any]:
    """Return the first element found in sequence that meets the predicate.

    Args:
        predicate (Callable[[Any], bool]): Predicate callback.
        sequence (Sequence): Iterable to search through.

    Returns:
        Optional[Any]: The element found. None if none met the predicate.
    """
    for item in sequence:
        if predicate(item):
            return item
    return None
