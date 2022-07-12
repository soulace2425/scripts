"""
test.py
11 July 2022 23:27:59

Anatomy for all command implementing files.
"""

from parser import Parser

import tekore as tk


class TestParser(Parser):
    pass


def callback(spotify: tk.Spotify) -> None:
    print("magic!")


def register_command(commands: dict[str, Parser]) -> None:
    parser = TestParser(callback)
    parser.register_command(commands)
