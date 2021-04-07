from __future__ import annotations

from asyncio import Queue, wait_for
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Optional,
)

from loguru import logger
from quara.core.errors import InvalidMessageError
from quara.core.types import Json

from .dependencies import get_callback_params
from .models import Message

if TYPE_CHECKING:  # pragma: no cover
    from .backend import BrokerBackend


class Subscription:
    def __init__(
        self,
        backend: BrokerBackend,
        subject: str,
        /,
        *,
        cb: Optional[Callable[..., Awaitable[Any]]] = None,
        **kwargs: Any,
    ) -> None:
        self._backend = backend
        self._subscription: Any = None
        self._delivery_queues: Dict[str, Queue[Message]] = {}
        self._connected: bool = False
        self.subject = subject
        if cb:
            self.cb = cb
            self._queue: Optional[Queue[Message]] = None
        else:
            self.cb = self.listener
            self._queue = Queue()
        self.options = kwargs

    async def start(self) -> None:
        """Start a subscrpition."""
        if self._connected:
            return
        else:
            self._subscription = await self._backend.subscribe(
                self.subject, cb=self._callback, **self.options
            )
            self._connected = True

    async def stop(self) -> None:
        """Stop a subscription."""
        if not self._connected:
            return
        await self._backend.unsubscribe(self)
        self._subscription = None
        self._connected = False

    async def listener(self, msg: Message) -> None:
        """Listenner that store messages in queues."""
        if self._queue is None:
            raise Exception("Listenner cannot be used with custom callback.")
        logger.debug(f"received new message on subject {msg.subject}")
        await self._queue.put(msg)
        for _, queue in self._delivery_queues.items():
            await queue.put(msg)

    async def next_message(self, timeout: Optional[int] = None) -> Message:
        """Wait for next message on subscription."""
        if self._queue is None:
            raise Exception("next_message() cannot be used with custom callback.")
        if timeout:
            return await wait_for(self._queue.get(), timeout=timeout)
        else:
            return await self._queue.get()

    def add_queue(self, name: str) -> Queue[Message]:
        """Add a new queue to the subscription."""
        if self._queue is None:
            raise Exception("Add queue cannot be used with custom callback.")
        if name in self._delivery_queues:
            raise ValueError(f"Queue {name} already exists.")
        queue = self._delivery_queues[name] = Queue()
        return queue

    async def __aiter__(self) -> AsyncIterator[Message]:
        """Iterate over subscription messages."""
        while True:
            yield await self.next_message()

    async def _reply(self, origin: Message, /, data: Optional[Json]) -> None:
        """Reply to a given message with given data."""
        if origin.reply:
            logger.debug(
                f"replying on subject {origin.reply} to request received on {origin.subject}"
            )
            await self._backend.publish(origin.reply, data=data)

    async def _callback(self, msg: Any) -> None:
        """Real callback used by the subscription."""
        try:
            # Parse message from received object
            message = Message.from_raw_msg(msg)
            logger.debug(
                f"Parsed message of {len(msg.data)} bytes on subject '{message.subject}'"
            )
        except InvalidMessageError as error:
            # Log error to stderr by default
            logger.error(error)
            raise error
        try:
            # Fetch all arguments as dict
            kwargs = get_callback_params(self.cb, message)
            # Execute callback
            logger.debug(
                f"Executing callback with arguments: {kwargs} on subject '{message.subject}'"
            )
            coro = self.cb(**kwargs)
            try:
                # Needed in case result is a coroutine
                result = await coro
            except TypeError:
                # If coro is not awaitable, then consider it as the result
                result = coro
        # Log any error encountered and raise error back
        except Exception as error:
            logger.error("An error occured during callback execution")
            # Raise error
            raise error
        # Try to reply
        try:
            await self._reply(message, result)
        # If any exception is raised, log it and raise it back
        except Exception as error:
            logger.error("An error occured during callback reply")
            raise error


__all__ = ["Subscription"]
