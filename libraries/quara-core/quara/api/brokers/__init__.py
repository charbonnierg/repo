"""Broker API.

This module exposes a class to work with message brokers.

Usage:

- Blocking example:

```
from quara.api.brokers import Broker


async def main():
    '''A simple example usage.'''
    # Use context manager to handle connection and disconnction
    async with Broker(backend="nats", host="localhost", port="4222") as broker:
        # Subscribe to some subject
        subscription = await broker.subscribe("demo.subject")
        # Block while waiting for messages
        async for message in subscription:
            # Publish on another subject when a message is received
            await broker.publish("another.subject", {"content": message.data})
```

- Non blocking example:

```
from quara.api.brokers import Broker, Message

broker = Broker(backend="nats", host="localhost", port="4222")

# Define subscription using decorator
# Note that subscription is not started using this syntax
@broker.subscribe("demo.subject")
async def my_callback(msg: Message):
    await broker.publish("another.subject", {"content": message.data})

async def main():
    # Start broker
    # This is what actually starts the subscription
    await broker.start()
```

"""
from .backend import BrokerBackend
from .client import Broker
from .context import BrokerContext
from .models import Message, Subject  # Do not expose TraceContext for the moment
from .subscription import Subscription

__all__ = [
    "Broker",
    "BrokerBackend",
    "BrokerContext",
    "Message",
    "Subject",
    "Subscription",
]
