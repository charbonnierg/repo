import collections.abc
from pathlib import Path
from typing import Any, Dict, Mapping, Union

import yaml


def deep_update(
    source: Dict[Any, Any], overrides: Mapping[Any, Any], /
) -> Dict[Any, Any]:
    """Perform a deep update using two dictionnaries.

    The second dictionnary is merged into the first one recursively.
    """
    for key, value in overrides.items():
        if isinstance(value, collections.Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source


def dict_from_yaml(path: Union[Path, str]) -> Dict[str, Any]:
    """Load a YAML file from given path."""
    # yaml.load might return other objects than dictionnary
    value = yaml.load(Path(path).read_bytes(), Loader=yaml.SafeLoader)
    # But this function is made specifically for dictionnaries
    if not isinstance(value, dict):
        raise ValueError(f"Cannot parse file {path} as a dictionnary")
    return value
