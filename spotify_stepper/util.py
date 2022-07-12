"""
util.py
12 July 2022 02:01:55
"""

from typing import Any, Callable, Iterable

import tekore as tk


def find(predicate: Callable, iterable: Iterable) -> Any | None:
    for item in iterable:
        if predicate(item):
            return item
    return None
