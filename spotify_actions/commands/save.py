"""
save.py
01 July 2022 21:10:02

Save music to a playlist.
"""

from typing import Any, Callable, Optional, Union

from base import Client, ParserBase

meta = {
    "name": "save",
    "description": "Save music to a playlist",
    "aliases": ()
}


class SaveParser(ParserBase):
    def __init__(self, func: Callable) -> None:
        super().__init__(func, **meta)

        self.add_argument("--track", "-t", default=None)
        self.add_argument("playlist", nargs="?", default=None)
        self.add_argument("--first", "-f", action="store_true")
        self.add_argument("--like", "-l", action="store_true")


def save(self,
         spotify: Client,
         track: Optional[str],
         playlist: Optional[str],
         first: bool,
         like: bool) -> None:
    pass


def register_command(commands: dict[str, ParserBase]) -> None:
    parser = SaveParser(save)
    parser.register_command(commands)
