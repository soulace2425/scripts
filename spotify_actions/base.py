"""
base.py
01 July 2022 20:53:02

Defines the base class for parsers.
"""

import shlex
from argparse import ArgumentParser, Namespace
from typing import Callable, Iterable, Optional, Sequence

from client import Client
from exceptions import CommandError


class ParserBase(ArgumentParser):
    """Base class for command parsers."""

    def __init__(self,
                 func: Callable,
                 name: str = None,
                 help: str = None,
                 aliases: Iterable[str] = None,
                 **kwargs) -> None:
        """Initialize command parser.

        Args:
            func (Callable): Callback associated with this command.
                Callback must take a Client instance as the first positional argument.
                The rest of the parameter list must match the arguments defined with add_argument().
            name (str, optional): Name of the command to appear in usage/help messages. Defaults to the callback name.
            help (str, optional): Description of the command to appear in help messages. Defaults to None.
            aliases (Iterable[str], optional): Aliases for this command. Defaults to None.
            **kwargs: Additional keyword arguments for argparse.ArgumentParser.
                prog and description are ignored as they are overriden by name and help respectively.
        """
        self._func = func
        self._name = name or func.__name__
        self._help = help
        self._aliases = set() if aliases is None else set(aliases)

        # prepend help with line with line [name|alias1|alias2|...]
        if len(self.aliases) > 0:
            self.aliases.discard(self.name)  # exclude from aliases
            aliases_str = "|" + "|".join(self.aliases)
        else:
            aliases_str = ""
        names_with_help = f"[{self.name}{aliases_str}] {self._help or ''}"

        kwargs.pop("prog", None)
        kwargs.pop("description", None)
        super().__init__(prog=self.name, description=names_with_help, **kwargs)

    @property
    def func(self) -> Callable:
        """Callback associated with this command."""
        return self._func

    @property
    def name(self) -> str:
        """Name of the command."""
        return self._name

    @property
    def help(self) -> str:
        """Description of the command"""
        return self._help

    @property
    def aliases(self) -> set[str]:
        """Aliases of the command."""
        return self._aliases

    def run_command(self, spotify: Client, args: Sequence[str]) -> bool:
        """Attempt to run the callback associated with this parser.

        Args:
            spotify (Client): Authenticated Spotify client.
            args (Sequence[str]): Arguments from the command line. Excludes the command name.

        Returns:
            bool: Whether parsing and execution succeeded.
        """
        # str.split() sometimes fails with shell syntax
        ns = self.parse_args(args)
        if ns is None:
            return False

        kwargs = ns.__dict__
        try:
            self.func(spotify, **kwargs)
        except CommandError as e:
            print(f"[Error] ({self.name}) {e}")
            return False
        return True

    def parse_args(self, args: Sequence[str]) -> Optional[Namespace]:
        """Override method to not exit the program when parsing fails.

        Args:
            args (Sequence[str]): Arguments from the command line.

        Returns:
            Optional[Namespace]: Generated Namespace. None if parsing fails.
        """
        try:
            return super().parse_args(args)
        except SystemExit:
            return None

    def register_command(self, commands: dict[str, "ParserBase"]) -> None:
        """Register self in the commands dict.

        Args:
            commands (dict[str, ParserBase]): Mapping to update.
        """
        commands[self.name] = self
        for name in self.aliases:
            commands[name] = self
