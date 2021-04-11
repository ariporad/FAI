from typing import *

from time import perf_counter

T = TypeVar('T')


def count(predicate: Callable[[T], bool], iterable: Iterable[Optional[T]]) -> int:
    return len(filter(predicate, iterable))


def is_unique(iterable: Iterable[T]) -> bool:
    lst = list(iterable)
    return len(set(lst)) == len(lst)


def print_each(iterable: Iterable[T], stringify=str, key=None):
    lines = sorted([stringify(item) for item in iterable], key=key)
    for line in lines:
        print(line)


def only(iterable: Iterable[T], message: Union[str, Exception] = "list expected to have length 1") -> Optional[T]:
    lst = list(iterable)
    assert len(lst) <= 1, message
    return lst[0] if len(lst) == 1 else None


def time(f):
    """
    Time the number of seconds it takes to run f.
    Returns a tuple: (time, f())
    """
    start = perf_counter()
    ret = f()
    end = perf_counter()
    return end - start, ret
    