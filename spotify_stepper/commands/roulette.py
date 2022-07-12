"""
roulette.py
12 July 2022 09:46:17
"""

import time
from collections import deque
from parser import Parser
from random import randrange

import tekore as tk
import util

#################
### CONSTANTS ###
#################

ANIMATION_COOLDOWN = 0.1  # seconds between playlist updates


###############################
### CALLBACK IMPLEMENTATION ###
###############################


def roulette(spotify: tk.Spotify, numtracks: int, reroll: int, zoom: bool) -> None:
    user = spotify.current_user()
    all_tracks = spotify.all_items(spotify.saved_tracks())
    util.printred(
        f"Loading all tracks from Liked Songs (this may take a while)...")
    saved_tracks = tuple(t.track.uri for t in all_tracks)

    playlist = spotify.playlist_create(user.id, "roulette",
                                       description="HTTP 429 speedrun any%")
    name = util.color(playlist.name, "cyan")
    print(f"Created playlist {name} with ID={playlist.id!r}.")

    def rand_idx() -> int:
        return randrange(0, len(saved_tracks))

    # initial numtracks tracks
    kept_tracks: deque[str] = deque(
        saved_tracks[rand_idx()] for _ in range(numtracks))

    # todo: prevent repeats?
    for uri in kept_tracks:
        spotify.playlist_add(playlist.id, (uri,))
        time.sleep(ANIMATION_COOLDOWN)
    # remove not taking effect for some reason, possibly InternalServerError
    while reroll > 0 or zoom:
        # discard track least recently added
        uri_to_delete = kept_tracks.popleft()
        spotify.playlist_remove(
            playlist.id, [uri_to_delete], playlist.snapshot_id)
        # append new track
        random_uri = saved_tracks[rand_idx()]
        spotify.playlist_add(playlist.id, (random_uri,))
        kept_tracks.append(random_uri)
        reroll -= 1
        time.sleep(ANIMATION_COOLDOWN)


############################
### COMMAND REGISTRATION ###
############################
meta = {
    "func": roulette,
    "name": "roulette",
    "help": "Roll and reroll some number of tracks in a roulette playlist",
    "aliases": None
}
"""Metadata for the roulette command."""


class RouletteParser(Parser):
    """Parser for the roulette command."""

    def __init__(self) -> None:
        super().__init__(**meta)
        self.add_argument("numtracks", type=int,
                          help="number of tracks in final playlist")
        self.add_argument("--reroll", "-r", type=int, default=0,
                          help="number of times to reroll a track")
        self.add_argument("--zoom", "-z", action="store_true",
                          help="HTTP 429 speedrun any%%")
        # DON'T USE AN UNESCAPED % FOR ARGPARSE LOL


def register_command(commands: dict[str, Parser]) -> None:
    """Required function to be called from main."""
    RouletteParser().register_command(commands)
