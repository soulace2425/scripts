"""
test.py
11 July 2022 23:27:59

Anatomy for all command implementing files.
"""

from parser import Parser
from typing import Callable

import tekore as tk


class TestParser(Parser):
    def __init__(self, func: Callable) -> None:
        super().__init__(func, "test", "Template command.", ("foo", "bar"))
        self.add_argument("--wow", "-w")


def callback(spotify: tk.Spotify, wow: str) -> None:
    print("magic!")
    print(f"{wow=}")


def register_command(commands: dict[str, Parser]) -> None:
    parser = TestParser(callback)
    parser.register_command(commands)
