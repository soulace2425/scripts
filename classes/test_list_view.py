"""
test_list_view.py
25 June 2022 02:51:13

Unit test file for list_view.py
"""

import unittest

from list_view import ListView


class TestListView(unittest.TestCase):
    """Unit tester class."""

    # @classmethod
    # def setUpClass(cls) -> None:
    #     return super().setUpClass()

    def setUp(self) -> None:
        self.src = [[i] for i in range(10)]
        self.view = ListView(self.src)


if __name__ == "__main__":
    unittest.main()
