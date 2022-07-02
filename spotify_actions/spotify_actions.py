#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spotify_actions.py
01 July 2022 09:17:30

Script for automating common actions in Spotify using tekore API wrapper.
"""

import os
import sys
from argparse import ArgumentParser, Namespace
from typing import Callable, NoReturn, Optional, Sequence

import tekore as tk
from dotenv import load_dotenv

# tekore read/write preferences
tk.client_id_var = "SPOTIFY_CLIENT_ID"
tk.client_secret_var = "SPOTIFY_CLIENT_SECRET"
tk.redirect_uri_var = "SPOTIFY_REDIRECT_URI"
tk.user_refresh_var = "SPOTIFY_REFRESH_TOKEN"

commands: dict[str, tuple[ArgumentParser, Callable]] = {}


class NoExitParser(ArgumentParser):
    def parse_args(self, args: Sequence[str] = None) -> Optional[Namespace]:
        try:
            return super().parse_args(args)
        except SystemExit:
            return None


class Quit(NoExitParser):
    def __init__(self) -> None:
        super().__init__(prog="quit", description="Quits the session")


def quit(ns: Namespace, spotify: tk.Spotify) -> NoReturn:
    print("quitting session")
    sys.exit(0)


class Clear(NoExitParser):
    def __init__(self) -> None:
        super().__init__(prog="clear", description="Clears the console screen")


def clear(ns: Namespace, spotify: tk.Spotify) -> None:
    os.system("cls")


class Save(NoExitParser):
    def __init__(self) -> None:
        super().__init__(prog="save", description="Saves a track to a playlist")
        self.add_argument("playlist", nargs="?", default=None,
                          help="name of playlist to save track to (defaults to current playlist)")
        self.add_argument("--track", "-t", default=None,
                          help="specify a track (defaults to current song)")
        self.add_argument("--like", "-l", action="store_true",
                          help="save track to Liked Songs as well")


def save(ns: Namespace, spotify: tk.Spotify) -> None:
    print(ns)


commands["quit"] = (Quit(), quit)
commands["clear"] = (Clear(), clear)
commands["save"] = (Save(), save)


def main() -> None:
    """Main driver function."""
    load_dotenv()

    creds = tk.config_from_environment(return_refresh=True)
    client_id, client_secret, _, user_refresh = creds
    token = tk.refresh_user_token(client_id, client_secret, user_refresh)
    spotify = tk.Spotify(token.access_token)

    display_name = spotify.current_user().display_name
    print(f"[Session] logged in as {display_name}")

    try:
        while True:
            command = input(f"{display_name}> ")
            args = command.split()
            if len(args) == 0:
                continue

            command_name, *command_args = args
            try:
                parser, func = commands[command_name]
            except KeyError as e:
                print(f"unknown command: {e}")
                continue

            ns = parser.parse_args(command_args)
            if ns is None:
                continue
            func(ns, spotify)
    except KeyboardInterrupt:
        print("[Session] quitting session")


if __name__ == "__main__":
    main()
