from time import perf_counter
from typing import *

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


def join_horizontal(strs: Iterator[str], joiner='', padding=' ') -> str:
    """
    Join multiple multiline strings horizontally:
    
    >>> print(join_horizontal(["foo\\nbar", "baz\\nqux"]))
    foobaz
    barqux
    """
    split_strs = [s.split('\n') for s in strs]
    all_strs_flat = [s for sublist in split_strs for s in sublist]
    maxlen = max(len(s) for s in all_strs_flat)
    return '\n'.join([joiner.join([p.ljust(maxlen, padding) for p in parts]) for parts in zip(*split_strs)])


# CITATION: This class is taken from my 1st Homework, and is originally heavily adapted from
# https://stackoverflow.com/a/3160819. Since a progress bar was completely unrelated to the point of this assignment, I
# felt it was acceptable and appropriate to not write the functionality myself.
class ProgressBar:
    """
    A command-line progress bar.
    """
    
    def __init__(self, width=50, progress=0, time=False):
        """
        Create a progress bar. This writes it to the console.
        """
        
        self.width = width
        self.progress = progress
        self.last_status = ""
        self.time = time
        self.start_time = perf_counter() if time else None
        self.update(progress, skip_erase=True)
    
    def update(self, progress, status="", skip_erase=False):
        """
        Update the progress bar, rewriting it to the console.
        """
        
        self.progress = progress
        
        if self.time:
            now = perf_counter()
            elapsed = self.format_time(now - self.start_time)
            remaining = self.format_time(((now - self.start_time) / self.progress) * (1 - self.progress)) if self.progress > 0 else "TBD"
            status += f" ({elapsed} elapsed, {remaining} remaining)"
        
        print(
            f"\r[{'█' * round(self.width * self.progress)}{' ' * round(self.width * (1 - self.progress))}] {status}{' ' * (max(0, len(self.last_status) - len(status)))}",
            end="", flush=True)
        
        self.last_status = status
    
    def stop(self, status=""):
        """
        Erase the progress bar from the console.
        """
        if status and self.time:
            status += f" Took {self.format_time(perf_counter() - self.start_time)}."
        print(f"\r{' ' * (self.width + 4 + len(self.last_status))}\r{status}", end=("\n" if status else ""), flush=True)
        self.last_status = status
    
    @staticmethod
    def format_time(seconds):
        """
        Format a number of seconds as a human-readable duration.
        
        >>> ProgressBar.format_time(5)
        '5s'
        >>> ProgressBar.format_time(75)
        '1m15s'
        >>> ProgressBar.format_time(120)
        '2m0s'
        >>> ProgressBar.format_time(131)
        '2m11s'
        >>> ProgressBar.format_time(3661)
        '1h1m1s'
        """
        seconds = round(seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600 :
            return f"{seconds // 60}m{seconds % 60}s"
        else:
            return f"{seconds // 3600}h{(seconds % 3600) // 60}m{seconds % 60}s"
            

def all_subclasses(cls):
    subclasses = cls.__subclasses__()
    return set(subclasses).union([subsub for sub in subclasses for subsub in all_subclasses(sub)])
