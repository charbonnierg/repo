from __future__ import annotations

from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from quara.core.errors import ClientNotConnectedError
from quara.core.plugins import Pluggable
from quara.core.types import Json

from .backend import BrokerBackend
from .context import BrokerContext
from .subscription import Subscription


class Broker(Pluggable[BrokerBackend]):
    """Backend Message Broker implementation for NATS.

    ### Notes:

    * By default the "nats" backend is used. It accepts the following arguments:
        - host: The listenning host of NATS server.
        - port: The listenning port of NATS server.
        - protocol: 'nats' or 'tls'.
        - servers: A list of servers URI. Takes precedence over host, port and protocol variables.
        - kwargs: See nats.py source code: <https://github.com/nats-io/nats.py/blob/master/nats/aio/client.py#L157>.

    * Connection to broker is performed only when calling the `Broker.connect()` method.

    * You can use the context manager to automatically close broker connections.

    ### Example usages:

    - Using a context manager:

    ```
    # Create broker using context manager
    async with Broker() as broker:
        # Do some work
        await broker.publish("some.subject", data={"some": "doc"})
    ```

    - Closing the connections manually:

    ```
    # Create database
    broker = Broker()
    # Connect manually
    await broker.connect()
    # Do some work
    sub = await broker.subscribe("some.other.subject")
    msg = await sub.next_message(timeout=1)
    # Close manually
    await broker.close()
    ```

    ### References:

    * nats.py Git Repository: <https://github.com/nats-io/nats.py>
    * NATS Docs -- Subject Based Messaging: <https://docs.nats.io/nats-concepts/subjects>
    * NATS Docs -- Publish/Subscribe: <https://docs.nats.io/nats-concepts/pubsub>
    * NATS Docs -- Request/Reply: <https://docs.nats.io/nats-concepts/reqreply>
    """

    __group__ = "quara.brokers"
    __default_backend__: str = "nats"

    def __init__(self, backend: Optional[str] = None, /, **kwargs: Any) -> None:
        """Create a new instance of Message Broker.

        By default "nats" backend is used.

        Arguments:
            backend: The backend implementation to use.
            kwargs: Additional keyword arguments forwarded to backend as options.

        Returns:
            None
        """
        super().__init__(backend, **kwargs)
        self._connected = False
        self._subscriptions: List[Subscription] = []

    async def start(self, **kwargs: Any) -> None:
        """Start message broker.

        This function will iterate over subscriptions and start them
        of that's not already done.

        Arguments:
            kwargs: Additional arguments forwared to the connect() method.
        """
        await self.connect(**kwargs)
        for sub in self._subscriptions:
            await sub.start()

    async def connect(self, **kwargs: Any) -> None:
        """Connect to the broker servers.

        Arguments:
            kwargs: Keyword arguments forwared to backend connect method.

        Returns:
            None
        """
        if not self._connected:
            await self._backend.connect(**kwargs)
            self._connected = True

    async def close(self, **kwargs: Any) -> None:
        """Close connection to the broker servers.

        Arguments:
            kwargs: Keyword arguments forwared to backend close method.

        Returns:
            None
        """
        if self._connected:
            await self._backend.close(**kwargs)
            self._connected = False

    async def __aenter__(self) -> Broker:
        """Asynchronous context manager."""
        await self.connect()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        """Asynchronous context manager exit."""
        await self.close()

    def _check_connection(self) -> None:
        if not self._connected:
            raise ClientNotConnectedError("Database client is not connected yet")

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
        self._check_connection()
        await self._backend.publish(subject, data=data, **kwargs)

    async def request(
        self,
        subject: str,
        /,
        data: Optional[Json] = None,
        *,
        timeout: int = 1,
        **kwargs: Any,
    ) -> Json:
        """Publish a message and expect a reply.

        Arguments:
            subject: The subject to publish to.
            data: The message paylaod. Must be JSON serializable.
            timeout: Optional timeout when performing request. Default to 1 second.
            kwargs: Additional keyword arguments given to backend client.

        Returns:
            Optionnally a vaild JSON serializable object (dict or list) replied by subscriber.
        """
        self._check_connection()
        return await self._backend.request(
            subject, data=data, timeout=timeout, **kwargs
        )

    async def subscribe(
        self,
        subject: str,
        *,
        cb: Optional[
            Callable[
                ..., Union[Coroutine[None, None, Json], Coroutine[None, None, None]]
            ]
        ] = None,
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
        self._check_connection()
        # Create subscription
        sub = Subscription(self._backend, subject, cb=cb, **kwargs)
        # Store subscription
        self._subscriptions.append(sub)
        # Start subscription
        await sub.start()
        # Return subscription
        return sub

    def on_message(
        self,
        subject: str,
        **kwargs: Any,
    ) -> Callable[
        [Callable[..., Coroutine[None, None, None]]],
        Callable[..., Coroutine[None, None, None]],
    ]:
        """Decorate a function to be used as an NATS subscription callback."""
        # on_message is a decorator that accepts decorator arguments and not the decorated function
        # the function below accepts the decorated function as argument
        def subscription_factory(
            cb: Callable[..., Coroutine[None, None, None]]
        ) -> Callable[..., Coroutine[None, None, None]]:
            """Create a subscription factory from a given callback."""
            # Create subscription
            sub = Subscription(self._backend, subject, cb=cb, **kwargs)
            # Store subscription
            self._subscriptions.append(sub)
            # Return function so that python does not complain
            # Note: The return value is never used
            return cb

        # Return subscription_factory which will act as decorator
        return subscription_factory

    @classmethod
    def from_context(
        cls, context: Union[BrokerContext, Dict[str, Any], None] = None
    ) -> Broker:
        """Create a new database from context."""
        if context:
            if isinstance(context, BrokerContext):
                options = context.dict(exclude_unset=True)
            else:
                options = context
        else:
            options = {}
        options.pop("enabled", None)
        return cls(**options)


__all__ = ["Broker"]
