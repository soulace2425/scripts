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
        self.view = ListView(self.src, 1, 8, 2)

    def test_properties(self) -> None:
        self.assertEqual(self.view.start, 1)
        self.assertEqual(self.view.stop, 8)
        self.assertEqual(self.view.step, 2)

    def test_converters(self) -> None:
        self.assertEqual(self.view.range, range(1, 8, 2))
        self.assertEqual(self.view.slice, slice(1, 8, 2))
        self.assertEqual(self.view.tuple, (1, 8, 2))

    def test_truthy(self) -> None:
        empty_view = ListView([])
        # __len__
        self.assertEqual(len(empty_view), 0)
        self.assertEqual(len(self.view), 4)
        # __bool__
        self.assertFalse(empty_view)
        self.assertTrue(self.view)

    def test_representations(self) -> None:
        # __str__
        self.assertEqual(
            str(self.view), f"ListView({self.src[self.view.slice]})")
        # __repr__
        self.assertEqual(repr(
            self.view), f"ListView(<list object at {hex(id(self.src))}>, start={self.view.start}, stop={self.view.stop}, step={self.view.step})")

    def test_iteration(self) -> None:
        for item, index in zip(self.view, self.view.range):
            self.assertIs(item, self.src[index])

    def test_getitem(self) -> None:
        for view_i, src_i in enumerate(self.view.range):
            self.assertIs(self.view[view_i], self.src[src_i])

    def test_setitem(self) -> None:
        new_value = ["used to be [5]"]
        self.view[2] = new_value
        self.assertIs(self.src[5], new_value)
        new_sequence = [["used to be [3]"], ["used to be [7]"]]
        self.view[1:4:2] = new_sequence
        self.assertIs(self.src[3], new_sequence[0])
        self.assertIs(self.src[7], new_sequence[1])

    def test_apply(self) -> None:
        sorted_values = [self.src[i] for i in self.view.range]
        sorted_values.reverse()
        self.view.apply(list.sort, key=lambda x: x[0], reverse=True)
        for test_i, src_i in enumerate(self.view.range):
            self.assertEqual(self.src[src_i], sorted_values[test_i])

    def test_for_each(self) -> None:
        self.view.for_each(lambda x: x.append(None))
        for item in self.view:
            self.assertIs(item[1], None)

    def test_map(self) -> None:
        result = self.view.map(lambda x: x[0]**2)
        for result_item, view_item in zip(result, self.view):
            self.assertEqual(result_item, view_item[0]**2)

    def test_filter(self) -> None:
        result = self.view.filter(lambda x: x[0] > 4)
        for item in self.view:
            if item[0] > 4:
                self.assertIn(item, result)
            else:
                self.assertNotIn(item, result)

    def test_shallow_copy(self) -> None:
        shallow_copy = list(self.view)
        print(all(shallow_copy[i] is self.src[j]
              for i, j in enumerate(self.view.range)))

    def test_deep_copy(self) -> None:
        deep_copy = self.view.deepcopy()
        print(all(deep_copy[i] is not self.src[j]
              for i, j in enumerate(self.view.range)))


if __name__ == "__main__":
    unittest.main()
