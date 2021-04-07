"""quara.api.brokers data models.

Classes defined in this module should be exported carefully in the top level of quara.api.brokers.

They might be not always be used by end users.
"""
from __future__ import annotations

import json
from collections import abc
from typing import Any, Optional

from pydantic import BaseModel
from quara.core.errors import InvalidMessageDataError, InvalidMessageError
from quara.core.types import Json, JsonModel


class Subject(str):
    """A subject is simply a string."""

    pass


class TraceContext(JsonModel):
    """A trace context contains 1 field named "traceparent"."""

    traceparent: Optional[str] = None


class Message(BaseModel):
    """Pydantic model denoting a message.

    Attributes:
        subject: The subject of the message.
        data: Message data as Json (dict or list).
        context: Message context (only holds trace context for now)
        reply: Message reply subject.
    """

    subject: Subject
    data: Optional[Json] = {}
    context: Optional[TraceContext] = TraceContext()
    reply: Optional[str] = ""

    @classmethod
    def from_raw_msg(cls, msg: Any) -> Message:
        """Parse a Message from a raw NATS message."""
        # Fetch message data
        try:
            data = msg.data
        except AttributeError:
            raise InvalidMessageError(f"Message does not have a data attribute: {msg}")
        # Decode bytes into string
        try:
            data_str = data.decode("utf-8")
        except (AttributeError, ValueError):
            raise InvalidMessageError(f"Message data is not valid utf-8 bytes: {msg}.")
        # Load dictionnary from JSON string
        try:
            content = json.loads(data_str)
        except (ValueError, TypeError):
            raise InvalidMessageError(
                f"Message data is not valid JSON message: {msg.data}"
            )
        # Fetch subject from message
        try:
            subject = msg.subject
        except AttributeError:
            raise InvalidMessageError(f"Message does not have a subject: {msg}")
        # Fetch reply from message
        try:
            reply = msg.reply
        except AttributeError:
            reply = ""
        # Check that content is an iterable
        # json module by defaults allows parsing bare integers or floats...
        if not isinstance(content, (abc.Mapping, abc.Sequence)):
            raise InvalidMessageDataError(
                "Message data should be an iterable or a mapping."
            )
        # json module parse all iterable
        if isinstance(content, abc.Sequence):
            context = None
            data = content
        # If we're here content is a mapping
        elif "__context__" in content:
            context = content.get("__context__")
            data = content.get("__data__")
            # If context is set but not data, raise an error
            if data is None:
                raise InvalidMessageDataError(
                    f"Message data has a __context__ field but not __data__field: {msg}"
                )
        # If there is no context consider the whole message content as data
        else:
            context = None
            data = content
        # Return a new instance of Message
        return cls.construct(
            context=context,
            data=data,
            subject=subject,
            reply=reply,
        )

    class Config:
        arbitrary_types_allowed = True


__all__ = ["Message", "Subject", "TraceContext"]
