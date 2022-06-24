#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
instagram_profile.py
23 June 2022 22:19:21

Simple script using web-scraping to update my Instagram
account profile with the HSSEAS day count.
"""

import time

from selenium import webdriver

INSTAGRAM_URL = "https://www.instagram.com/direct/inbox/"


def main() -> None:
    """Main driver function."""
    # remember to update Edge browser itself to match driver version
    # MicrosoftEdgeDriver.exe in a PATH directory: Python/Python39/Scripts
    driver = webdriver.Edge()
    driver.get(INSTAGRAM_URL)

    while True:
        time.sleep(0.1)


if __name__ == "__main__":
    main()
