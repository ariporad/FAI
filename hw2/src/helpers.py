from typing import *

T = TypeVar('T')


def count(predicate: Callable[[T], bool], iterable: Iterable[Optional[T]]) -> int:
    return len(filter(predicate, iterable))


def is_unique(iterable: Iterable[T]) -> bool:
    return len(set(iterable)) == len(iterable)


def print_each(iterable: Iterable[T], stringify=str, key=None):
    lines = sorted([stringify(item) for item in iterable], key=key)
    for line in lines:
        print(line)


def only(iterable: Iterable[T], message: Union[str, Exception] = "list expected to have length 1") -> Optional[T]:
    lst = list(iterable)
    assert len(lst) <= 1, message
    return lst[0] if len(lst) == 1 else None
