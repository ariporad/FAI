from typing import *

T = TypeVar('T')
def count(predicate: Callable[[T], bool], iterable: Iterable[Optional[T]]) -> int:
	return len(filter(predicate, iterable))

def is_unique(iterable: Iterable[T]) -> bool:
	return len(set(iterable)) == len(iterable)