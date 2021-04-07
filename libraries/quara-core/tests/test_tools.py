from pathlib import Path

import pytest
from quara.core.dicts import deep_update, dict_from_yaml


@pytest.mark.core
def test_deep_update_add() -> None:
    source = {"hello1": 1}
    overrides = {"hello2": 2}
    deep_update(source, overrides)
    assert source == {"hello1": 1, "hello2": 2}


@pytest.mark.core
def test_deep_update_overwrite() -> None:
    source = {"hello": "to_override"}
    overrides = {"hello": "over"}
    deep_update(source, overrides)
    assert source == {"hello": "over"}


@pytest.mark.core
def test_deep_update_mixed() -> None:
    source = {"hello": {"value": "to_override", "no_change": 1}}
    overrides = {"hello": {"value": "over"}}
    deep_update(source, overrides)
    assert source == {"hello": {"value": "over", "no_change": 1}}


@pytest.mark.core
def test_deep_update_overwrite_nested_int_to_dict() -> None:
    source = {"hello": {"value": "to_override", "no_change": 1}}
    overrides = {"hello": {"value": {}}}  # type: ignore
    deep_update(source, overrides)
    assert source == {"hello": {"value": {}, "no_change": 1}}


@pytest.mark.core
def test_deep_update_overwrite_nested_dict_to_dict() -> None:
    source = {"hello": {"value": {}, "no_change": 1}}
    overrides = {"hello": {"value": 2}}
    deep_update(source, overrides)
    assert source == {"hello": {"value": 2, "no_change": 1}}


@pytest.mark.core
def test_load_yaml_file(test_files_directory: Path) -> None:
    content = dict_from_yaml(test_files_directory / "test.yml")
    assert content["broker"]["host"] == "127.0.0.1"
    assert content["extra_options"]["name"] == "test"
