#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
roller_gui.pyw
22 June 2022 22:21:10

GUI entry point to waifu_roller/roller.py.
"""

import os

import pyautogui as pag

ROLLER_PATH = "roller.py"


def main() -> None:
    """Main driver function."""
    response = pag.prompt(
        text="python roller.py",
        title="Supply command line arguments",
        default="wa -c digimon-waifus -n 16"
    )
    os.system(f"python {ROLLER_PATH} {response}")


if __name__ == "__main__":
    main()
