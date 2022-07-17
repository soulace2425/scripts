"""
client.py
12 July 2022 21:02:18
"""

import tekore as tk
from dotenv import load_dotenv

# Read/write preferences
tk.client_id_var = "SPOTIFY_CLIENT_ID"
tk.client_secret_var = "SPOTIFY_CLIENT_SECRET"
tk.redirect_uri_var = "SPOTIFY_REDIRECT_URI"
tk.user_refresh_var = "SPOTIFY_REFRESH_TOKEN"


class Client:
    def __init__(self) -> None:
        self._tk = self._login()

    def _login(self) -> tk.Spotify:
        load_dotenv()
        # use tekore wrapper to manage authentication
        credentials = tk.config_from_environment(
            return_refresh=True)
        self._client_id = credentials[0]
        self._client_secret = credentials[1]
        self._redirect_uri = credentials[2]
        self._refresh_token = credentials[3]
        token = tk.refresh_user_token(
            self._client_id, self._client_secret, self._refresh_token)
        return tk.Spotify(token.access_token)

    def get_user(self, id: str, /):
        pass


def main() -> None:
    """Main driver function."""
    # test code
    client = Client()
    print(type(client._tk.token))


if __name__ == "__main__":
    main()
