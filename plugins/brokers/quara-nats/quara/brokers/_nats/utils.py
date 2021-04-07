from json import dumps
from typing import Any

from quara.core.types import Json


def to_payload(data: Json, **kwargs: Any) -> bytes:
    if data or data in ([], {}):
        return dumps(data, **kwargs).encode("utf-8")
    return "{}".encode("utf-8")
