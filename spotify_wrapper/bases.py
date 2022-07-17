"""
bases.py
12 July 2022 21:48:54
"""

from typing import Any, Callable, Literal

import requests

from client import Client

ResponseDict = dict[str, Any]

HTTPMethod = Literal["get", "post", "put", "patch", "delete"]


class Model:
    def __init__(self, client: Client) -> None:
        self._client = client

    def make_request(self, method: HTTPMethod, url: str, params: dict = None, headers: dict = None) -> requests.Response:
        func: Callable = eval(f"requests.{method.lower()}")
        return func(url, params=params, headers=headers)


m = Model()
r = m.make_request("get", "https://google.com")
print(r)
