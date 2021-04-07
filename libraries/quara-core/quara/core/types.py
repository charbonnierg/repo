from typing import Mapping, Sequence, Union

from pydantic import BaseModel

# A single value can either be a string, a float, an int, a bool, or None
_JsonValue = Union[str, float, int, bool, None]
# A field can either be a single value, or a mapping of keys and values, or a sequence of values
_JsonField = Union[
    _JsonValue,
    Mapping[str, _JsonValue],
    Sequence[_JsonValue],
]
# A field can contains a sequence of fields or a mapping of keys and fields
JsonField = Union[_JsonField, Sequence[_JsonField], Mapping[str, _JsonField]]
# A document is a mapping of keys and fields or a sequence of fields
Json = Union[Mapping[str, JsonField], Sequence[JsonField]]


class JsonModel(BaseModel):
    """A base model class that can be easily serialized to JSON."""

    class Config:
        extra = "allow"


class StrictJsonModel(JsonModel):
    """A base model class that can be easily serialized to JSON."""

    class Config:
        extra = "forbid"


__all__ = ["Json", "JsonModel", "StrictJsonModel"]
