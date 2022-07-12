"""
exceptions.py
12 July 2022 03:05:37
"""


class CommandError(Exception):
    pass


class CommandNotFound(CommandError):
    pass
