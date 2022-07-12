"""
step.py
12 July 2022 01:45:11
"""

import difflib
from parser import Parser
from typing import Generator

import PyInquirer
import tekore as tk
import util
from colorama import Back, Fore, Style
from exceptions import CommandError

###############################
### CALLBACK IMPLEMENTATION ###
###############################


def _get_playlist_from_query(spotify: tk.Spotify, query: str) -> tk.model.SimplePlaylist:
    """Get the first user-owned playlist that resembles query.

    Args:
        spotify (tk.Spotify): Authenticated client instance.
        query (str): Playlist name query to match.

    Raises:
        CommandError: Could not resolve playlist from query.

    Returns:
        tk.model.SimplePlaylist: Playlist most closely matching query.
    """
    user_id = spotify.current_user().id
    result = spotify.playlists(user_id)
    playlists = {pl.name: pl for pl in result.items}
    matches = difflib.get_close_matches(query, playlists.keys(), n=1)
    if len(matches) == 0:
        raise CommandError(
            f"Could not find any of your playlists with query {query!r}")
    return playlists[matches[0]]


TrackGenerator = Generator[tk.model.SavedTrack |
                           tk.model.PlaylistTrack, None, None]
"""Type alias for return type of spotify.all_items."""


def _get_tracks(spotify: tk.Spotify, playlist: list[str]) -> tuple[str, TrackGenerator, int, bool]:
    """Resolve playlist from command line arg playlist.

    Args:
        spotify (tk.Spotify): Authenticated client instance.
        playlist (list[str]): Playlist name (argument from command line).

    Raises:
        CommandError: Could not resolve playlist from query.

    Returns:
        tuple[str, TrackGenerator, int, bool]: Name of the playlist, a generator yielding tracks of the playlist, total number of tracks in playlist, and whether this playlist is the user's Liked Songs.
    """
    # use Liked Songs
    if len(playlist) == 0:
        playlist_name = "Liked Songs"
        paging = spotify.saved_tracks()
        using_liked = True
    # find the first user-owned playlist that matches query
    else:
        query = " ".join(playlist)
        pl = _get_playlist_from_query(spotify, query)
        playlist_name = pl.name
        # SimplePlaylist -> FullPlaylist
        paging = spotify.playlist(pl.id).tracks
        using_liked = False
    all_tracks = spotify.all_items(paging)
    num_tracks = paging.total
    return (playlist_name, all_tracks, num_tracks, using_liked)


def _confirm_playlist(playlist_name: str) -> bool:
    """Prompt user for confirmation if playlist is the correct one.

    Args:
        playlist_name (str): Name of playlist to step through.

    Returns:
        bool: Whether user answered yes.
    """
    print(f"Stepping through playlist {Fore.CYAN}{playlist_name}{Fore.RESET}.")
    question = {
        "type": "confirm",
        "name": "wanted",
        "message": "Is this the one you wanted?",
        "default": True
    }
    answers = PyInquirer.prompt((question,))
    return answers["wanted"]


def step(spotify: tk.Spotify, playlist: list[str]) -> None:
    """Callback for the step command.

    Args:
        spotify (tk.Spotify): Authenticated client instance.
        playlist (list[str]): (CL arg) Playlist name. An empty list denotes Liked Songs.
    """
    playlist_name, all_tracks, num_tracks, using_liked = _get_tracks(
        spotify, playlist)

    if not using_liked:
        if not _confirm_playlist(playlist_name):
            print(
                f"{Fore.RED}Try running the command again with a more specific query.")
            return

    for num, track in enumerate(all_tracks, start=1):
        progress = f"{num}/{num_tracks}"
        name = track.track.name
        name = util.color(name, "blue")
        artists = ", ".join(artist.name for artist in track.track.artists)
        artists = util.color(artists, "cyan")
        print(f"({progress}) {name} by {artists}")
        action = input("> ")  # todo


############################
### COMMAND REGISTRATION ###
############################


meta = {
    "func": step,
    "name": "step",
    "help": "Step through every song in a playlist for further action",
    "aliases": None
}
"""Metadata for the step command."""


class StepParser(Parser):
    """Parser for the step command."""

    def __init__(self) -> None:
        super().__init__(**meta)
        self.add_argument("playlist", nargs="*")


def register_command(commands: dict[str, Parser]) -> None:
    """Required function to be called from main."""
    StepParser().register_command(commands)
