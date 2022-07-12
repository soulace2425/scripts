"""
util.py
12 July 2022 02:01:55
"""

from typing import Any, Callable, Iterable

import tekore as tk
from colorama import Back, Fore, Style


def printred(message: str, intensity: int = 1) -> None:
    """Print message in red.

    Intensity options:
        - 0 or lower: uncolored, unstyled text
        - 1: red text (+colorama.Fore.RED)
        - 2: emphasized red text (+colorama.Style.BRIGHT)
        - 3 or higher: red background (colorama.Back.RED)

    Args:
        message (str): Message to print.
        intensity (int, optional): Determines style of red to use (see above). Defaults to 1.
    """
    codes = ""
    if intensity == 1:
        codes = Fore.RED
    elif intensity == 2:
        codes = Fore.RED + Style.BRIGHT
    elif intensity >= 3:
        codes = Back.RED
    print(f"{codes}{message}")


def color(string: str, color_name: str) -> str:
    """Color text of input string.

    Args:
        string (str): Text to color.
        color_name (str): Name of colorama constant (e.g. 'blue' or 'BLUE').

    Returns:
        str: Input string wrapped with appropriate ANSI escape sequences.
    """
    # resolve colorama color
    c = eval(f"Fore.{color_name.upper()}")
    return f"{c}{string}{Fore.RESET}"


def find(predicate: Callable, iterable: Iterable, default: Any = None) -> Any:
    """Return the first item in iterable that meets the predicate.

    Args:
        predicate (Callable): Predicate to test each item of iterable.
        iterable (Iterable): Iterable to search through.
        default (Any, optional): Value to return if no item is found. Defaults to None.

    Returns:
        Any: First item in iterable that meets the predicate, or default value if none found.
    """
    for item in iterable:
        if predicate(item):
            return item
    return default
