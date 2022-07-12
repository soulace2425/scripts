"""
step.py
12 July 2022 01:45:11
"""


import difflib
from parser import Parser
from typing import Callable

import tekore as tk
from colorama import Back, Fore, Style
from exceptions import CommandError
from tabulate import tabulate

meta = {
    "name": "step",
    "help": "Step through every song in a playlist for further action",
    "aliases": None
}


class StepParser(Parser):
    def __init__(self, func: Callable) -> None:
        super().__init__(func, **meta)
        self.add_argument("playlist", nargs="*")


def _get_playlist_from_query(spotify: tk.Spotify, query: str) -> tk.model.SimplePlaylist | None:
    user_id = spotify.current_user().id
    result = spotify.playlists(user_id)
    playlists = {pl.name: pl for pl in result.items}
    matches = difflib.get_close_matches(query, playlists.keys(), n=1)
    if len(matches) == 0:
        return None
    return playlists[matches[0]]


def step(spotify: tk.Spotify, playlist: list[str]) -> None:
    # find the first user-owned playlist that matches query
    if len(playlist) > 0:
        query = " ".join(playlist)
        pl = _get_playlist_from_query(spotify, query)
        if pl is None:
            raise CommandError(
                f"Could not find any of your playlists with query {query!r}")
        playlist_name = pl.name
        # SimplePlaylist -> FullPlaylist
        paging = spotify.playlist(pl.id).tracks
    # use Liked Songs
    else:
        playlist_name = "Liked Songs"
        paging = spotify.saved_tracks()

    print(f"{Fore.CYAN}{playlist_name}:")
    for num, track in enumerate(spotify.all_items(paging), start=1):
        track: tk.model.PlaylistTrack | tk.model.SavedTrack = track
        print(
            f"{num:03} {Fore.BLUE}{track.track.name}{Fore.RESET} added on {track.added_at:%b %d, %Y}")


def register_command(commands: dict[str, Parser]) -> None:
    parser = StepParser(step)
    parser.register_command(commands)
