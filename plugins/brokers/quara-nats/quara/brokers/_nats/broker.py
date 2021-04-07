from typing import Any, Awaitable, Callable, List, Optional

# NATS related imports
from nats.aio.client import Client as NC
from nats.aio.errors import ErrTimeout
from quara.api.brokers import BrokerBackend, Message, Subscription
from quara.core.types import Json

from .utils import to_payload


class AsyncioNatsBroker(BrokerBackend):
    """Backend Message Broker implementation for NATS.

    ### References:

    * nats.py Git Repository: <https://github.com/nats-io/nats.py>
    * NATS Docs -- Subject Based Messaging: <https://docs.nats.io/nats-concepts/subjects>
    * NATS Docs -- Publish/Subscribe: <https://docs.nats.io/nats-concepts/pubsub>
    * NATS Docs -- Request/Reply: <https://docs.nats.io/nats-concepts/reqreply>
    """

    __backend__ = "nats"

    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 4222,
        tls: bool = False,
        servers: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new instance of NATS Message Broker backend.

        Arguments:
            host: Hostname of NATS server to reach.
            port: Port of NATS server to reach.
            protocol: Protocol to use (`nats` or `tls`)
            servers: A list of servers to connect to. If given, host, port and protocol arguments are ignore.
            kwargs: Additional keyword arguments forwarded as NATS connection options.

        Returns:
            None
        """
        # servers takes precedence over manually constructed server URI
        servers = servers or [f"{'tls' if tls else 'nats'}://{host}:{port}"]
        self.connect_options = {"servers": servers, **kwargs}
        self._nc = NC()

    async def connect(self, **kwargs: Any) -> None:
        """Connect to the NATS servers.

        Arguments:
            kwargs: All keyword arguments are ignored

        Returns:
            None
        """
        # Additional kwargs are ignored
        await self._nc.connect(**self.connect_options)

    async def close(self, **kwags: Any) -> None:
        """Close the connection to NATS servers.

        Arguments:
            kwargs: All keyword arguments are ignored

        Returns:
            None
        """
        # Additional kwargs are ignored
        await self._nc.close()

    async def publish(
        self, subject: str, /, data: Optional[Json] = None, **kwargs: Any
    ) -> None:
        """Publish message to NATS.

        Arguments:
            subject: The subject to publish to.
            data: The payload to send in message. Must be JSON serializable.
            kwargs: Additional keyword arguments given to nats backend client.

        Returns:
            None
        """
        # Additional kwargs are not used
        # They are only present to ensure compatibility between backends
        await self._nc.publish(subject, to_payload(data))

    async def request(
        self,
        subject: str,
        /,
        data: Optional[Json] = None,
        *,
        timeout: int = 1,
        **kwargs: Any,
    ) -> Json:
        """Publish message to NATS and expect a reply.

        Arguments:
            subject: The subject to publish to.
            data: The message paylaod. Must be JSON serializable.
            timeout: Optional timeout when performing request. Default to 1 second.
            kwargs: Additional keyword arguments given to nats backend client.

        Returns:
            Optionnally a vaild JSON serializable object (dict or list) replied by subscriber.
        """
        # Request using NATS
        try:
            _reply: Any = await self._nc.request(
                subject, payload=to_payload(data), timeout=timeout, **kwargs
            )
        except ErrTimeout:
            raise TimeoutError(f"No reply received in {timeout} seconds")
        # Parse response
        reply = Message.from_raw_msg(_reply)
        # Return response data only if it's not an empty dict
        return reply.data

    async def subscribe(
        self,
        subject: str,
        *,
        cb: Optional[Callable[..., Awaitable[Any]]] = None,
        **kwargs: Any,
    ) -> int:
        """Subscribe to an NATS subject.

        Arguments:
            subject: The subject to susbcribe to.
            cb: The callback to use. If no callback is given, subscription will store messages in a queue.
            kwargs: Additional arguments forwarded to NATS subscribe method.

        Returns:
            An integer denoting the created subscription ID.
        """
        # I think this is going to change in the future!
        sub: int = await self._nc.subscribe(subject, cb=cb, **kwargs)
        return sub

    async def unsubscribe(self, subscription: Subscription, **kwargs: Any) -> None:
        """Stop an NATS subscription.

        Arguments:
            subscription: Subscription to stop
            kwargs: Additional keyword arguments forwarded to NATS unsubscribe method.

        Returns:
            None
        """
        # NATS consider subscription as integers (for the moment!)
        await self._nc.unsubscribe(subscription._subscription, **kwargs)
