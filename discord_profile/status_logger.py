#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
status_logger.py
11 July 2022 00:07:43

Selenium script for extracting and logging Discord custom status.
"""

import argparse
import csv
import sys

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

# reuse code lol
from discord_profile import DISCORD_URL, find_status_input, login, setup

WAIT_TIMEOUT = 5.0  # seconds


class Parser(argparse.ArgumentParser):
    def __init__(self) -> None:
        super().__init__(description="CLI for status_logger.py")
        self.add_argument("--headless", "-l", action="store_true",
                          help="run the driver headlessly (no window popup)")


def extract_status(status_input: WebElement) -> str:
    pass


def save_status(self, status: str) -> None:
    pass


def main() -> None:
    """Main driver function."""
    ns = Parser().parse_args(sys.argv[1:])

    driver = setup(ns.headless)

    driver.get(DISCORD_URL)
    # wait for page to load
    driver.implicitly_wait(WAIT_TIMEOUT)

    login(driver)
    status_input = find_status_input(driver)
    status = extract_status(status_input)
    save_status(status)

    print("successfully executed process")
    driver.quit()
    print("successfully terminated script")


if __name__ == "__main__":
    main()
