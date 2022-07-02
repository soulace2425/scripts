#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
01 July 2022 09:17:30

Script for automating common actions in Spotify using tekore API wrapper.
"""

import importlib
import os
import shlex
import sys

import tekore as tk
from dotenv import load_dotenv

from base import ParserBase
from client import Client

# tekore read/write preferences
tk.client_id_var = "SPOTIFY_CLIENT_ID"
tk.client_secret_var = "SPOTIFY_CLIENT_SECRET"
tk.redirect_uri_var = "SPOTIFY_REDIRECT_URI"
tk.user_refresh_var = "SPOTIFY_REFRESH_TOKEN"

COMMANDS_PATH = "commands/"


def login() -> Client:
    """Load credentials from .env and log into Spotify.

    Returns:
        Client: Authenticated Spotify client.
    """
    load_dotenv()
    creds = tk.config_from_environment(return_refresh=True)
    client_id, client_secret, _, user_refresh = creds
    token = tk.refresh_user_token(client_id, client_secret, user_refresh)
    return Client(token.access_token)


def register_commands() -> dict[str, ParserBase]:
    """Register all commands defined in the COMMANDS_PATH directory.

    Returns:
        dict[str, ParserBase]: Mapping of command name/alias to parser instance.
    """
    commands = {}
    for file_name in os.listdir(COMMANDS_PATH):
        if not file_name.endswith(".py"):
            continue
        module_name = file_name.removesuffix(".py")
        dot_path = COMMANDS_PATH.replace("/", ".") + module_name
        module = importlib.import_module(dot_path)
        module.register_command(commands)
    return commands


def prompt_save(spotify: Client) -> None:
    """Prompt if user wants to save session variables.

    Args:
        spotify (Client): Authenticated Spotify client.
    """
    # prompt for save
    while True:
        try:
            choice = input(
                "[Session] would you like to save this session? (y/n) ")
        except KeyboardInterrupt:
            print("\n[^C] cancelled")
            return
        choice = choice.lower()
        if choice in ("y", "yes"):
            break
        # need an explicit n/no to be safe
        if choice in ("n", "no"):
            return

    # attempt to save
    try:
        spotify.save_session()
        print(
            f"[Session] successfully saved session to {spotify.default_path}")
    except ValueError:
        print("[Session] no default path found for client")

    # prompt for manual path
    while True:
        try:
            path = input(
                "[Session] path of the file to create/overwrite (Ctrl+C to cancel): ")
        except KeyboardInterrupt:
            print("\n[^C] cancelled")
            return
        if path == "":
            continue
        try:
            spotify.save_session(path)
            return
        except OSError:
            print(f"[Error] couldn't write to {path=}")


def main_loop(spotify: Client, commands: dict[str, ParserBase]) -> None:
    """Run CLI session.

    Args:
        spotify (Client): Authenticated Spotify client.
    """
    display_name = spotify.current_user().display_name
    print(f"[Session] logged in as {display_name}")

    try:
        while True:
            s = input(f"{display_name}> ")
            if s == "" or s.isspace():
                continue
            args = shlex.split(s)
            name = args[0]
            parser = commands[name]
            parser.run_command(spotify, args[1:])
    except KeyboardInterrupt:
        print("\n[^C]")
        prompt_save(spotify)
        print("[Session] quitting session")
        sys.exit(0)


def main() -> None:
    """Main driver function."""
    spotify = login()
    commands = register_commands()
    main_loop(spotify, commands)


if __name__ == "__main__":
    main()
