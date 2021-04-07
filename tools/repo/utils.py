from __future__ import annotations

import contextlib
import os
import pathlib
import subprocess
import sys
from typing import Iterator


@contextlib.contextmanager
def current_directory(path: pathlib.Path) -> Iterator[pathlib.Path]:
    """Context manager to temporary go into a specific directory."""
    old_dir = os.getcwd()
    try:
        os.chdir(str(path))
        yield path
    finally:
        os.chdir(old_dir)


def run(cmd: str) -> None:
    """Run a command in shell mode and exit on error."""
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError:
        sys.exit(1)
