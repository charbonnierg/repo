from pathlib import Path

from quara.core.path import current_directory


def test_current_directory():
    test_filepath = Path(__file__)
    with current_directory(test_filepath.parent) as d:
        assert test_filepath.name in [_file.name for _file in Path(".").glob("*")]
        assert Path(".").absolute() == d.absolute()
