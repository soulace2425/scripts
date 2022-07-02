#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test.py
02 July 2022 01:00:43

Testing script. Not part of final product.
"""

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

results = spotify.search("coding mix", types=("playlist",))
result: tk.model.SimplePlaylistPaging = results[0]
coding_mix = find(lambda item: item.owner.display_name ==
                  "Vincent Lin", result.items)
print(coding_mix)
