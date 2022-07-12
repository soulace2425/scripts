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
from exceptions import CommandError

#################
### CONSTANTS ###
#################

Track = tk.model.SavedTrack | tk.model.PlaylistTrack
"""Type alias for types of tracks that command can deal with."""

TrackGenerator = Generator[Track, None, None]
"""Type alias for return type of spotify.all_items."""

# for-each actions
ACTION_SKIP = "Skip"
ACTION_VIEW = "View information"
ACTION_ADD = "Add to preset"

# preset playlists (by ID)
# todo: make this programmatic
PRESET_CN = "1RPJbcJJAr5NbJXok00kSf"
PRESET_JP = "4GknCaIa62xLeEq1MxGPAe"
PRESET_KR = "4AApsy06U5xbZB1IFlKom0"
PRESET_SP = "27e31bddkFpy0p100DDtYt"

###############################
### CALLBACK IMPLEMENTATION ###
###############################

# temp fix: to be initialized upon first step command
user_playlists = []


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
        paging = spotify.playlist_items(pl.id)
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
    print(f"Stepping through playlist {util.color(playlist_name, 'cyan')}.")
    question = {
        "type": "confirm",
        "name": "wanted",
        "message": "Is this the one you wanted?",
        "default": True
    }
    answers = PyInquirer.prompt((question,))
    return answers["wanted"]


def _prompt_action() -> str:
    question = {
        "type": "expand",
        "name": "choice",
        "message": "What action would you like to take?",
        "choices": [
            {
                "key": "s",
                "name": ACTION_SKIP
            },
            {
                "key": "v",
                "name": ACTION_VIEW
            },
            {
                "key": "a",
                "name": ACTION_ADD
            }
        ]
    }
    answers = PyInquirer.prompt((question,))
    try:
        choice = answers["choice"]
    # answers == {} if canceled during prompt
    except KeyError:
        raise KeyboardInterrupt from None
    return choice


def _view_track(track: Track) -> None:
    # todo: nasty global var solution lmao
    def track_in_playlist(d: dict) -> bool:
        items = d["tracks"]["items"]
        return util.find(lambda i: i["track"]["id"] == track.track.id, items)

    properties = {
        "Title":
            track.track.name,
        "Artists":
            ", ".join(a.name for a in track.track.artists),
        "Added":
            track.added_at.strftime("%Y-%b-%d %H:%M:%S"),
        "Included in playlists":
            "\n" + "\n".join(d["name"]
                             for d in user_playlists if track_in_playlist(d))
    }

    for prop, val in properties.items():
        prop = util.color(prop, "magenta")
        print(f"{prop}: {val}")
    print()


def _prompt_preset() -> list[str]:
    question = {
        "type": "checkbox",
        "name": "presets",
        "message": "Which preset(s) to add to?",
        "choices": [
            {
                "name": "CN",
                "value": PRESET_CN
            },
            {
                "name": "JP",
                "value": PRESET_JP
            },
            {
                "name": "KR",
                "value": PRESET_KR
            },
            {
                "name": "SP",
                "value": PRESET_SP
            }
        ]
    }
    answers = PyInquirer.prompt((question,))
    try:
        presets = answers["presets"]
    # answers == {} if canceled during prompt
    except KeyError:
        raise KeyboardInterrupt from None
    return presets


def _add_to_preset(spotify: tk.Spotify, track: Track) -> None:
    presets = _prompt_preset()
    playlist_names = []
    for preset_id in presets:
        spotify.playlist_add(preset_id, (track.track.uri,))
        playlist = spotify.playlist(preset_id, "name")
        playlist_name = util.color(playlist["name"], "cyan")
        playlist_names.append(playlist_name)
    track_name = util.color(track.track.name, "blue")
    print(f"Added {track_name} to {', '.join(playlist_names)}")


def _execute_action(spotify: tk.Spotify, choice: str, track: Track) -> None:
    if choice == ACTION_VIEW:
        _view_track(track)
        # recurse: don't continue stepping yet
        print()
        choice = _prompt_action()
        _execute_action(spotify, choice, track)
    elif choice == ACTION_ADD:
        _add_to_preset(spotify, track)


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
            util.printred(
                f"Try running the command again with a more specific query.")
            return

    # temp fix: process user's saved playlists if first time
    if len(user_playlists) == 0:
        simple_pls = spotify.playlists(spotify.current_user().id)
        simple_pls = spotify.all_items(simple_pls)
        util.printred("Processing your playlists (this may take a while)...")
        dict_pls = [spotify.playlist(pl.id, "name,tracks.items(track.id)")
                    for pl in simple_pls]
        user_playlists.extend(dict_pls)

    # note: it seems httpx.RemoteProtocolError can be raised mid-iteration
    for num, track in enumerate(all_tracks, start=1):
        progress = f"{num}/{num_tracks}"
        name = track.track.name
        name = util.color(name, "blue")
        artists = ", ".join(artist.name for artist in track.track.artists)
        artists = util.color(artists, "cyan")
        print(f"\n({progress}) {name} by {artists}")
        choice = _prompt_action()
        _execute_action(spotify, choice, track)

    # generator exhausted
    print(
        f"\nDone stepping through playlist {util.color(playlist_name, 'cyan')}!")


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
