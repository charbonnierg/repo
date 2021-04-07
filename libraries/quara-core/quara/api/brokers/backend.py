from __future__ import annotations

from abc import abstractmethod
from typing import Any, Awaitable, Callable, Optional

from quara.core.plugins import Plugin
from quara.core.types import Json

from .subscription import Subscription


class BrokerBackend(Plugin):
    @abstractmethod
    def __init__(self, **kwargs: Any) -> None:
        """Create a new instance of Message Broker backend.

        Arguments:
            kwargs: Additional keyword arguments forwarded to backend as options.

        Returns:
            None
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def connect(self, **kwargs: Any) -> None:
        """Connect to the broker servers.

        Arguments:
            kwargs: Keyword arguments forwared to backend connect method.

        Returns:
            None
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def close(self, **kwargs: Any) -> None:
        """Close connection to the broker servers.

        Arguments:
            kwargs: Keyword arguments forwared to backend close method.

        Returns:
            None
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def publish(
        self, subject: str, /, data: Optional[Json] = None, **kwargs: Any
    ) -> None:
        """Publish message to NATS.

        Arguments:
            subject: The subject to publish to.
            data: The payload to send in message. Must be JSON serializable.
            kwargs: Additional keyword arguments given to backend client.

        Returns:
            None
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def request(
        self,
        subject: str,
        /,
        data: Optional[Json] = None,
        *,
        timeout: int = 1,
        **kwargs: Any,
    ) -> Optional[Json]:
        """Publish a message and expect a reply.

        Arguments:
            subject: The subject to publish to.
            data: The message paylaod. Must be JSON serializable.
            timeout: Optional timeout when performing request. Default to 1 second.
            kwargs: Additional keyword arguments given to backend client.

        Returns:
            Optionnally a vaild JSON serializable object (dict or list) replied by subscriber.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def subscribe(
        self,
        subject: str,
        *,
        cb: Optional[Callable[..., Awaitable[Any]]] = None,
        **kwargs: Any,
    ) -> Subscription:
        """Subscribe to a given subject.

        Arguments:
            subject: The subject to susbcribe to.
            cb: The callback to use. If no callback is given, subscription will store messages in a queue.
            kwargs: Additional keyword arguments given to backend client.

        Returns:
            A subscription object.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def unsubscribe(self, subscription: Subscription, **kwargs: Any) -> None:
        """Stop an NATS subscription.

        Arguments:
            subscription: Subscription to stop
            kwargs: Additional keyword arguments forwarded to backend unsubscribe method.

        Returns:
            None
        """
        raise NotImplementedError  # pragma: no cover
