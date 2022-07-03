"""
client.py
01 July 2022 23:31:11
"""

import pickle
from typing import Any, NoReturn

import tekore as tk


class Client(tk.Spotify):
    """tekore.Spotify class extended to save session variables."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the Spotify client.

        Args:
            *args: Positional arguments for tk.Spotify.
            **kwargs: Keyword arguments for tk.Spotify.
        """
        super().__init__(*args, **kwargs)
        self._session = {}
        self._default_path = ""
        self._human = self.current_user()

    @property
    def session(self) -> dict[str, Any]:
        """Namespace for client session."""
        return self._session

    @property
    def default_path(self) -> str:
        """Default read/write path for pickling client session."""
        return self._default_path

    @property
    def human(self) -> tk.model.PrivateUser:
        """The user account the client is logged in as."""
        return self._human

    @default_path.setter
    def default_path(self, new_path: str) -> None:
        self._default_path = new_path

    def _raise_no_path(self) -> NoReturn:
        """Raise ValueError when read/write path cannot be resolved."""
        raise ValueError("no path provided and no default_path found")

    def save_session(self, path: str = None) -> None:
        """Pickle client session to path.

        Args:
            path (str, optional): Path to write to. Defaults to default_path.
        """
        path = path or self.default_path or self._raise_no_path()
        with open(path, "wb") as file:
            pickle.dump(self.session, file)

    def load_session(self, path: str = None) -> None:
        """Unpickle client session from path.

        Args:
            path (str, optional): Path to read from. Defaults to default_path.
        """
        path = path or self.default_path or self._raise_no_path()
        with open(path, "rb") as file:
            self._session = pickle.load(file)
