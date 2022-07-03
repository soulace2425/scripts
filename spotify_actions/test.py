#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test.py
02 July 2022 01:00:43

Testing script. Not part of final product.
"""

import pickle
from typing import Any, Callable, Iterable

import tekore as tk
from dotenv import load_dotenv

##### SETUP #####

# tekore read/write preferences
tk.client_id_var = "SPOTIFY_CLIENT_ID"
tk.client_secret_var = "SPOTIFY_CLIENT_SECRET"
tk.redirect_uri_var = "SPOTIFY_REDIRECT_URI"
tk.user_refresh_var = "SPOTIFY_REFRESH_TOKEN"

load_dotenv()
creds = tk.config_from_environment(return_refresh=True)
client_id, client_secret, _, user_refresh = creds
token = tk.refresh_user_token(client_id, client_secret, user_refresh)
spotify = tk.Spotify(token.access_token)


def find(predicate: Callable[[Any], Any], iterable: Iterable) -> Any:
    for item in iterable:
        if predicate(item):
            return item
    return None


##### TESTS #####

user = spotify.current_user()
result = spotify.search("dsagfshadsgkahslgash", types=("track",))
model_list = result[0].items
for item in model_list:
    print(item)
