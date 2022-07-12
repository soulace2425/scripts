#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
11 July 2022 22:43:44

CLI for stepping through every song in Liked Songs.
"""

import colorama
import tekore as tk
from colorama import Fore
from dotenv import load_dotenv

CLI_PROMPT = f"{Fore.GREEN}(Spotify) {Fore.RESET}"
EXIT_COMMANDS = ("q", "quit", "exit")


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


def main_loop(spotify: tk.Spotify) -> None:
    try:
        colorama.init(autoreset=True)
        while True:
            command = input(CLI_PROMPT)
            if command == "" or command.isspace():
                continue
            if command.lower() in EXIT_COMMANDS:
                raise KeyboardInterrupt
            print(f"{command=}")
    # don't break loop
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
    # gracefully exit
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Aborted!")
    finally:
        colorama.deinit()


def main() -> None:
    """Main driver function."""
    import_credentials()
    spotify = login_to_spotify()
    main_loop(spotify)


if __name__ == "__main__":
    main()
