#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
11 July 2022 22:43:44

CLI for stepping through every song in Liked Songs.
"""

import importlib
import os
import shlex
from parser import Parser

import colorama
import tekore as tk
from colorama import Back, Fore, Style
from dotenv import load_dotenv

CLI_PROMPT = f"{Fore.GREEN}(Spotify) {Fore.RESET}"
EXIT_WORDS = ("q", "quit", "exit")


def import_credentials() -> None:
    """Load credentials from .env file to os.environ."""
    # tk credential read/write preferences
    tk.client_id_var = "SPOTIFY_CLIENT_ID"
    tk.client_secret_var = "SPOTIFY_CLIENT_SECRET"
    tk.redirect_uri_var = "SPOTIFY_REDIRECT_URI"
    tk.user_refresh_var = "SPOTIFY_REFRESH_TOKEN"
    load_dotenv()


def login_to_spotify() -> tk.Spotify:
    """Log in to Spotify as Vincent Lin and return authenticated client."""
    credentials = tk.config_from_environment(return_refresh=True)
    client_id, client_secret, _, user_refresh = credentials
    token = tk.refresh_user_token(client_id, client_secret, user_refresh)
    return tk.Spotify(token.access_token)


def register_commands() -> dict[str, Parser]:
    commands = {}
    for file_name in os.listdir("commands/"):
        if file_name.endswith(".py"):
            module_name = file_name.removesuffix(".py")
            import_path = f"commands.{module_name}"
            module = importlib.import_module(import_path)
            # every command implementation file should have a
            # register_command function
            try:
                module.register_command(commands)
            except AttributeError:
                print(
                    f"{Fore.RED}SETUP ERROR: implementation file {file_name!r} does not have a register_command function")
                print(
                    f"{Fore.RED}Skipping registration of any commands defined in {file_name}")
    return commands


def main_loop(spotify: tk.Spotify, commands: dict[str, Parser]) -> None:
    user = spotify.current_user()
    print(f"Welcome, {user.display_name}!")
    try:
        while True:
            line = input(CLI_PROMPT)
            if line == "" or line.isspace():
                continue
            name, *args = shlex.split(line)
            name = name.lower()
            # check exit words before commands
            # this means any commands named/aliased with such words
            # will become masked in the main_loop
            if name in EXIT_WORDS:
                raise KeyboardInterrupt
            try:
                command = commands[name]
                command.run_command(spotify, args)
            except KeyError:
                print(f"{Fore.RED}Command {name!r} not found")
            print(f"{line=}")
    # don't break loop
    except Exception as e:
        print(f"{type(e).__name__}: {e}")


def main() -> None:
    """Main driver function."""
    colorama.init(autoreset=True)
    try:
        import_credentials()
        spotify = login_to_spotify()
        commands = register_commands()
        main_loop(spotify, commands)
    # gracefully exit (catches KeyboardInterrupt)
    except:
        print(f"{Fore.RED}Aborted!")
    finally:
        colorama.deinit()


if __name__ == "__main__":
    main()
