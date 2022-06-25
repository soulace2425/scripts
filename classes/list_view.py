"""
list_view.py
25 June 2022 01:24:58

Implements the ListView class, an attempt at implementing mutable
sublists ("views") of the builtin list.

Also implements imitations of the higher-order JavaScript methods,
for_each, map, and filter
"""

import copy
from typing import Any, Callable, Iterator, Union

# Type Aliases
ListIndex = Union[int, slice]


class ListView:
    """Mutable sublist of a target list."""

    __slots__ = ("_source", "_start", "_step", "_stop")

    def __init__(self, source: list, start: int = 0, stop: int = ..., step: int = 1) -> None:
        self._source = source
        self._start = start
        self._step = step
        self._stop = len(source) if stop is ... else stop

    # **************************************************
    #                   PROPERTIES
    # **************************************************

    @property
    def source(self) -> list:
        """The list that this view tracks."""
        return self._source

    @property
    def start(self) -> int:
        """The start index of the target list that the view tracks."""
        return self._start

    @property
    def stop(self) -> int:
        """The stop index of the target list that the view tracks."""
        return self._stop

    @property
    def step(self) -> int:
        """The stride of the view within the target list."""
        return self._step

    @property
    def address(self) -> int:
        """The memory address of the target list."""
        return id(self.source)

    # **************************************************
    #                   CONVERTERS
    # **************************************************

    @property
    def range(self) -> range:
        """The start, stop, and step properties as a range object."""
        return range(self.start, self.stop, self.step)

    @property
    def slice(self) -> slice:
        """The start, stop, and step properties as a slice object."""
        return slice(self.start, self.stop, self.step)

    @property
    def tuple(self) -> tuple:
        """The start, stop, and step properties as a 3-tuple."""
        return (self.start, self.stop, self.step)

    def deepcopy(self) -> list:
        """Return a deepcopy of the viewed sublist as a list.

        Use this instead of `list(view)` when elements need to be copied recursively.
        """
        return copy.deepcopy(self.source[self.slice])

    # **************************************************
    #               HELPER METHODS
    # **************************************************

    def _calc_src_slice(self, view_slice: slice) -> slice:
        """Helper function for converting a view slice to a slice for the underlying list.

        Args:
            view_slice (slice): The desired slice of the view.

        Returns:
            slice: The equivalent slice of the underlying list.
        """
        start = view_slice.start
        stop = view_slice.stop
        step = view_slice.step
        s = slice(self.start + start * self.step,
                  self.start + stop * self.step,
                  self.step * step)
        return s

    def _calc_src_index(self, view_index: int) -> int:
        """Helper function for converting a view index to an index for the underlying list.

        Args:
            view_index (int): The desired index of the view.

        Returns:
            int: The equivalent index of the underlying list.
        """
        return self.start + view_index * self.step

    # **************************************************
    #           ACCESSING AND MUTATING
    # **************************************************

    def __getitem__(self, index: ListIndex) -> Union[list, Any]:
        if isinstance(index, int):
            i = self._calc_src_index(index)
            return self.source[i]
        elif isinstance(index, slice):
            s = self._calc_src_slice(index)
            return self.source[s]
        else:
            raise TypeError(
                f"{self.__class__.__name__} indices must be integers, or slices, not {index.__class__.__name__}")

    def __setitem__(self, index: ListIndex, value: Any) -> None:
        if isinstance(index, int):
            i = self._calc_src_index(index)
            self.source[i] = value
        elif isinstance(index, slice):
            s = self._calc_src_slice(index)
            self.source[s] = value
        else:
            raise TypeError(
                f"{self.__class__.__name__} indices must be integers, or slices, not {index.__class__.__name__}")

    def __iter__(self) -> Iterator:
        return (self.source[i] for i in self.range)

    # **************************************************
    #           BUILTIN FUNCTION DUNDERS
    # **************************************************

    def __len__(self) -> int:
        return len(self.range())

    def __bool__(self) -> bool:
        return len(self) > 0

    def __str__(self) -> str:
        return f"ListView({self.source[self.slice]})"

    def __repr__(self) -> str:
        return f"ListView(<list object at {hex(id(self.source))}>, start={self.start}, stop={self.stop}, step={self.step})"

    # def __add__(self, obj: Any) -> "ListView":
    #     if not isinstance(obj, self.__class__):
    #         return NotImplemented
    #     if obj.source is not self.source:
    #         raise ValueError("iterators do not target the same list")
    #     if obj.step != self.step:
    #         raise ValueError("iterators do not share the same step")
    #     start = min(self.start, obj.start)
    #     stop = max(self.stop, obj.stop)
    #     result = self.__class__(self.source, start, stop)
    #     return result

    # def __iadd__(self, obj: Any) -> "ListView":
    #     if not isinstance(obj, self.__class__):
    #         return NotImplemented
    #     if obj.source is not self.source:
    #         raise ValueError("iterators do not target the same list")
    #     if obj.step != self.step:
    #         raise ValueError("iterators do not share the same step")
    #     self._start = min(self.start, obj.start)
    #     self._stop = max(self.stop, obj.stop)
    #     return self

    # def __lshift__(self, amount: int) -> "ListView":
    #     new_start = max(self.start - amount, 0)
    #     new_stop = self.stop - amount
    #     result = self.__class__(self.source, new_start,
    #                             new_stop, self.step)
    #     return result

    # def __rshift__(self, amount: int) -> "ListView":
    #     result = self.__class__(self.source, self.start + amount,
    #                             self.stop + amount, self.step)
    #     return result

    # **************************************************
    #               HIGHER ORDER METHODS
    # **************************************************

    def apply(self, callback: Callable, *args: Any, **kwargs: Any) -> Any:
        """Apply a function with the viewed sublist as an argument.

        Example:
            ```
            src = [i for i in range(10)]
            view = ListView(src, 3, 8)
            view.apply(list.sort, reverse=True)
            print(src)  # [1, 2, 7, 6, 5, 4, 3, 8, 9]
            ```

        Args:
            callback (Callable): The function to call with the view as the first positional argument.
            *args (Any): Additional positional arguments to supply to `callback`.
            **kwargs (Any): Keyword arguments to supply to `callback`.

        Returns:
            Any: The return value of `callback`.
        """
        copy = self.source[self.slice]
        retval = callback(copy, *args, **kwargs)
        self.source[self.slice] = copy
        return retval

    def for_each(self, callback: Callable[[Any], Any]) -> None:
        """Imitation of the Array.forEach method.

        Args:
            callback (Callable): Function to call with each list element as an argument.
        """
        for item in self:
            callback(item)

    def map(self, callback: Callable[[Any], Any]) -> list:
        return [callback(item) for item in self]

    def filter(self, predicate: Callable[[Any], bool]) -> list:
        return [item for item in self if predicate(item)]


def test_code() -> None:
    """Place test code here."""
    src = [[i] for i in range(10)]
    view = ListView(src, 1, 8, 2)
    for item, index in zip(view, view.range):
        print(item, item is src[index])

    print(view.slice)
    print(view.tuple)

    view[2] = "this changed!"
    print(src)

    view[2] = [5]  # restore

    view.apply(list.sort, key=lambda x: x[0], reverse=True)
    print(src)

    view.for_each(lambda x: x.append(None))
    print(src)

    result = view.map(lambda x: [x[1]]*x[0])
    print(result)

    result = view.filter(lambda x: x[0] > 4)
    print(result)

    shallow_copy = list(view)
    print(shallow_copy)
    print(all(shallow_copy[i] is src[j] for i, j in enumerate(view.range)))

    deep_copy = view.deepcopy()
    print(deep_copy)
    print(all(deep_copy[i] is not src[j] for i, j in enumerate(view.range)))


if __name__ == "__main__":
    test_code()
