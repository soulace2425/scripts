#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
endian.py
01 July 2022 01:56:34

Simple visualizer for integer storage on different endian
architectures.
"""

import sys
from collections import namedtuple

NumType = namedtuple("NumType", ("size", "signed"))

type_map = {
    "int8": NumType(1, True),
    "int16": NumType(2, True),
    "int32": NumType(3, True),
    "int64": NumType(4, True),
    "uint8": NumType(1, False),
    "uint16": NumType(2, False),
    "uint32": NumType(3, False),
    "uint64": NumType(4, False),
}


def process_overflow(num: int, numtype: NumType) -> int:
    size, signed = numtype
    if not signed and num < 0:
        tmin = -2**(size-1)
        num %= tmin
        umax = 2**size
        num = umax + 1 + num


def get_byte_array(num: int, numtype: NumType) -> list[int]:
    size, signed = numtype


def main() -> None:
    """Main driver function."""
    pass


if __name__ == "__main__":
    main()
