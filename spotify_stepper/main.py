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
import subprocess
from parser import NULL_PARSER, Parser

import colorama
import tekore as tk
from colorama import Back, Fore, Style
from dotenv import load_dotenv

from exceptions import CommandError, CommandNotFound

CLI_PROMPT = f"{Fore.GREEN}(Spotify) {Fore.RESET}"
EXIT_WORDS = ("q", "quit", "exit")
CLEAR_WORDS = ("cls", "clear")
HELP_MESSAGE = f"Spotify CLI! Use one of {EXIT_WORDS} or ^C to exit. Use 'list' to view list of commands."


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


def list_commands(commands: dict[str, Parser]) -> None:
    unique_parsers = set(commands.values())
    for parser in unique_parsers:
        print(f"{parser.name:>10} | {parser.help}")


def main_loop(spotify: tk.Spotify, commands: dict[str, Parser]) -> None:
    user = spotify.current_user()
    os.system("cls")
    print(f"{Fore.GREEN}Welcome, {user.display_name}!")

    while True:
        # get and split input
        line = input(CLI_PROMPT)
        if line == "" or line.isspace():
            continue
        name, *args = shlex.split(line)
        name = name.lower()

        # check special exit words before commands
        # this means any commands named/aliased with such words
        # will become masked in the main_loop
        if name == "help":
            print(HELP_MESSAGE)
            continue
        if name == "list":
            list_commands(commands)
            continue
        if name in CLEAR_WORDS:
            os.system("cls")
            continue
        if name in EXIT_WORDS:
            raise KeyboardInterrupt
        if name == "python":
            print(f"{Fore.RED}Started a Python subprocess:")
            py = subprocess.Popen("python -q")
            retcode = py.wait()
            print(f"{Fore.RED}Python subprocess exited with code {hex(retcode)}.")
            continue

        # retrieve and run parser
        try:
            command = commands.get(name, NULL_PARSER)
            command.run_command(spotify, args)
        # command was NULL_PARSER
        except CommandNotFound:
            print(f"{Fore.RED}Command {name!r} not found")
        # some expected error occurred
        except CommandError as e:
            print(f"{Fore.RED}{e}")
        # some unexpected Python error occurred
        except Exception as e:
            print(f"{Back.RED}An unexpected Python error occurred:")
            print(f"{Fore.RED}{type(e).__name__}: {e}")
            print(
                f"{Fore.RED}{Style.BRIGHT}Aborting further action for command {name!r}, resuming program.")

        print(f"{line=}")  # debug


def main() -> None:
    """Main driver function."""
    colorama.init(autoreset=True)
    try:
        import_credentials()
        spotify = login_to_spotify()
        commands = register_commands()
        main_loop(spotify, commands)
    # gracefully exit
    except KeyboardInterrupt:
        print(f"{Fore.RED}Quitting program!")
    except Exception as e:
        print(f"{Back.RED}An unexpected Python error occurred:")
        print(f"{Fore.RED}{type(e).__name__}: {e}")
        print(f"{Fore.RED}{Style.BRIGHT}Aborting program.")
    finally:
        colorama.deinit()


if __name__ == "__main__":
    main()
