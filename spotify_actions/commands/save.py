"""
save.py
01 July 2022 21:10:02

Save music to a playlist.
"""

from typing import Any, Callable, NoReturn, Optional, Union

import tekore as tk
from base import Client, ParserBase
from exceptions import CommandError

meta = {
    "name": "save",
    "help": "Save music to a playlist",
    "aliases": ()
}


class SaveParser(ParserBase):
    def __init__(self, func: Callable) -> None:
        super().__init__(func, **meta)

        self.add_argument("playlist", nargs="?", default=None,
                          help="name of playlist to save to; if omitted, uses playing playlist or Liked Songs")
        self.add_argument("--track", "-t", default=None,
                          help="name of track to add; if omitted, uses playing track")
        self.add_argument("--first", "-f", action="store_true",
                          help="skip search results by automatically choosing the first option")
        self.add_argument("--like", "-l", action="store_true",
                          help="save track to Liked Songs in addition to chosen playlist")


def _raise_no_track() -> NoReturn:
    raise CommandError(
        "no track specified and no track detected in current playback")


def _display_results(result: tuple[tk.model.Paging, ...]) -> None:
    print("<display results>")  # todo


def _get_track_id(spotify: Client, query: str, first: bool) -> str:
    result = spotify.search(
        query, types=("track",))
    if first:
        first_page: tk.model.FullTrackPaging = result[0]
        first_track = first_page.items[0]
        return first_track.id
    _display_results(result)
    print("<prompt user input>")  # todo
    return "7tzPzs6GUueoIaZHBgN1rG"  # todo (孤单北半球)


def _get_playlist_id(spotify: Client, query: str, first: bool) -> str:
    result = spotify.search(query, types=("playlist",))
    if first:
        first_page: tk.model.SimplePlaylistPaging = result[0]
        first_playlist = first_page.items[0]
        return first_playlist.id
    _display_results(result)
    print("<prompt user input>")  # todo
    return "5FpuSaX0kDeItlPMIIYBZS"  # todo (coding mix)


def _pb_track_id(pb: Optional[tk.model.CurrentlyPlayingContext]) -> Optional[str]:
    if pb is None or pb.item is None:
        return None
    _, track_id = tk.from_uri(pb.item.uri)
    return track_id


def _pb_playlist_id(pb: Optional[tk.model.CurrentlyPlayingContext]) -> Optional[str]:
    if pb is None or pb.context is None:
        return None
    type, id = tk.from_uri(pb.context.uri)
    if type != "playlist":
        return None
    return id


def save(spotify: Client,
         track: Optional[str],
         playlist: Optional[str],
         first: bool,
         like: bool) -> None:
    """save [PLAYLIST] [--track TRACK] [--first] [--like]

    Args:
        spotify (Client): Authenticated Spotify client.
        track (Optional[str]): Track query. If None, use currently playing track. If none, raise CommandError.
        playlist (Optional[str]): Playlist query. If None, use currently playing playlist. If none, use Liked Songs.
        first (bool): Flag for automatically taking the first choice from query results.
        like (bool): Flag for adding the track to Liked Songs in addition to chosen playlist (does nothing if playlist already resolves to Liked Songs).

    Raises:
        CommandError: No track specified and no track detected in current playback.
    """
    pb = spotify.playback()

    # resolve track ID from: track query > current pb track > fail
    if track is not None:
        track = _get_track_id(spotify, track, first)
    else:
        track = _pb_track_id(pb) or _raise_no_track()

    # resolve playlist ID from: playlist query > current pb playlist > (use Liked Songs)
    if playlist is not None:
        playlist = _get_playlist_id(spotify, playlist, first)
    else:
        playlist = _pb_playlist_id(pb) or ...  # flag to use Liked Songs

    print(track, playlist)


def register_command(commands: dict[str, ParserBase]) -> None:
    parser = SaveParser(save)
    parser.register_command(commands)
