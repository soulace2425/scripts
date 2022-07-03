"""
save.py
01 July 2022 21:10:02

Save music to a playlist.
"""

from typing import Any, Callable, NoReturn, Optional, Union

import tekore as tk
from base import Client, ParserBase
from exceptions import CommandError
from tabulate import tabulate

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


def _raise_no_playlist() -> NoReturn:
    raise CommandError(
        "the specified playlist could not be found or does not belong to you")


def _display_track_results(result: tuple[tk.model.FullTrackPaging, ...]) -> list[tk.model.FullTrack]:
    track_list = result[0].items
    entries = [None] * len(track_list)
    if len(entries) == 0:
        print("no results returned")
        return []
    for index, track in enumerate(track_list, start=1):
        entry = [index, track.name, ", ".join(a.name for a in track.artists)]
        entries[index-1] = entry
    table = tabulate(entries, headers=("Index", "Track Name",
                     "Artist Names"), tablefmt="github")
    print(table)
    return track_list


def _prompt_track_choice(track_list: list[tk.model.FullTrack]) -> tk.model.FullTrack:
    max_index = len(track_list)
    while True:
        choice = input(
            f"enter index of the track you mean to choose (1-{max_index}): ")
        try:
            chosen_index = int(choice)
            if chosen_index not in range(1, max_index+1):
                raise IndexError
        except ValueError:
            print("invalid input! please enter a valid index number")
            continue
        except IndexError:
            print(f"index out of range! please enter a valid index")
            continue
        else:
            chosen_track = track_list[chosen_index-1]
            print(chosen_track.name)
            return chosen_track


def _display_playlist_results(result: tuple[tk.model.SimplePlaylistPaging, ...],
                              spotify: Client) -> list[tk.model.SimplePlaylist]:
    # filter by playlists that belong to the user
    playlist_list = [
        pl for pl in result[0].items if pl.owner.id == spotify.human.id]
    entries = [None] * len(playlist_list)
    if len(entries) == 0:
        print("no results returned")
        return []
    for index, playlist in enumerate(playlist_list, start=1):
        shortened = playlist.description[:27]
        if shortened != playlist.description:
            shortened += "..."
        entry = [index, playlist.name, shortened]
        entries[index-1] = entry
    table = tabulate(entries, headers=("Index", "Playlist Name",
                     "Description"), tablefmt="github")
    print(table)
    return playlist_list


def _prompt_playlist_choice(playlist_list: list[tk.model.SimplePlaylist]) -> tk.model.SimplePlaylist:
    max_index = len(playlist_list)
    while True:
        choice = input(
            f"enter index of the track you mean to choose (1-{max_index}): ")
        try:
            chosen_index = int(choice)
            if chosen_index not in range(1, max_index+1):
                raise IndexError
        except ValueError:
            print("invalid input! please enter a valid index number")
            continue
        except IndexError:
            print(f"index out of range! please enter a valid index")
            continue
        else:
            chosen_playlist = playlist_list[chosen_index-1]
            print(chosen_playlist.name)
            return chosen_playlist


def _get_track_id(spotify: Client, query: str, first: bool) -> Optional[str]:
    result = spotify.search(
        query, types=("track",))
    if first:
        first_page: tk.model.FullTrackPaging = result[0]
        first_track = first_page.items[0]
        return first_track.id
    track_list = _display_track_results(result)
    if len(track_list) == 0:
        return None
    chosen_track = _prompt_track_choice(track_list)
    return chosen_track.id


def _get_playlist_id(spotify: Client, query: str, first: bool) -> Optional[str]:
    result = spotify.search(query, types=("playlist",))
    if first:
        first_page: tk.model.SimplePlaylistPaging = result[0]
        # find first playlist that belongs to user
        for playlist in first_page.items:
            if playlist.owner.id == spotify.human.id:
                return playlist.id
        return None
    playlist_list = _display_playlist_results(result, spotify)
    if len(playlist_list) == 0:
        return None
    chosen_playlist = _prompt_playlist_choice(playlist_list)
    return chosen_playlist.id


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
        CommandError: No track specified and no track detected in current playback. Or, no playlist found if specified.
    """
    pb = spotify.playback()

    # resolve track ID from: track query > current pb track > fail
    if track is not None:
        track = _get_track_id(spotify, track, first) or _raise_no_track()
    else:
        track = _pb_track_id(pb) or _raise_no_track()

    # resolve playlist ID from: playlist query > current pb playlist > (use Liked Songs)
    if playlist is not None:
        playlist = _get_playlist_id(
            spotify, playlist, first) or _raise_no_playlist()
    else:
        playlist = _pb_playlist_id(pb) or ...  # flag to use Liked Songs

    if playlist == ... or like:
        spotify.saved_tracks_add([track])
        print(f"added {tk.to_url('track', track)} to Liked Songs")
        if playlist == ...:
            return  # no further action
    spotify.playlist_add(playlist, [tk.to_uri("track", track)])
    print(
        f"added {tk.to_url('track', track)} to {tk.to_url('playlist', playlist)}")


def register_command(commands: dict[str, ParserBase]) -> None:
    parser = SaveParser(save)
    parser.register_command(commands)
