from contextlib import contextmanager
from os import chdir
from pathlib import Path
from typing import Iterator, Union


@contextmanager
def current_directory(path: Union[str, Path]) -> Iterator[Path]:
    """Useful context manager to change current directory.

    Example usage:
        >>> with current_directory("/tmp"):
        >>>     # You're in /tmp directory
        >>>     print(os.cwd())
        >>> # You're no longer in /tmp directory
        >>> print(os.cwd())
    """
    old_dir = Path.cwd()
    cur_dir = Path(path)
    try:
        chdir(cur_dir)
        yield cur_dir
    finally:
        chdir(old_dir)
