# type: ignore[misc]
import asyncio
from typing import List

import pytest
from quara.api import Broker, Message, Subject
from quara.core.errors import (
    InvalidMessageDataError,
    InvalidMessageError,
    PluginNotFoundError,
)
from quara.core.types import JsonModel


@pytest.mark.asyncio
@pytest.mark.brokers
def test_bad_backend() -> None:
    with pytest.raises(PluginNotFoundError):
        Broker("natssss")


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_default_backend(broker: Broker) -> None:
    assert broker._connected
    # Connecting twice shoud not raise an error
    await broker.connect()
    # Disconnecting twice should not raise an error
    await broker.close()
    await broker.close()


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_start_stop(broker: Broker) -> None:
    assert broker._connected
    await broker.start()
    await broker.start()
    assert broker._connected
    await broker.close()
    assert not broker._connected

    @broker.on_message("test_start_stop")
    async def cb(msg: Message):
        return {}

    await broker.start()
    await broker.start()


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_default_listenner(broker: Broker) -> None:
    # Create a subscription
    sub = await broker.subscribe("test_default_listenner")
    # Ensure that timeout works well when getting next message
    with pytest.raises(asyncio.TimeoutError):
        await sub.next_message(timeout=0.1)
    # Add a new queue to subscription
    other_queue = sub.add_queue("test_queue")
    # You cannot add the same queue twice
    with pytest.raises(ValueError):
        sub.add_queue("test_queue")
    # Queue should not process invalid messages
    with pytest.raises(InvalidMessageError):

        class BadMessage:
            pass

        await sub._callback(BadMessage())

    # Queue should process published messages
    await broker.publish("test_default_listenner")
    # And forward all messages to its delivery queues
    async for message in sub:
        msg = await other_queue.get()
        assert message == msg
        break
    # Once subscription is stopped
    await sub.stop()
    # _subscription attribute is None
    assert sub._subscription is None
    # _connected attribute is None
    assert not sub._connected
    # Stopping again shouldn't cause an error
    await sub.stop()


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_publish_empty(broker: Broker) -> None:
    # Create a subscription
    sub = await broker.subscribe("testsub_empty")
    # Publish a message
    await broker.publish("testsub_empty")
    # Received message from subscription
    received = await sub.next_message()
    # Validate message data and subject
    assert received.subject == "testsub_empty"
    assert received.data == {}


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_publish_data(broker: Broker) -> None:
    # Create a subscription
    sub = await broker.subscribe("testsub_data")
    # Publish a message with some data
    await broker.publish(
        "testsub_data",
        {
            "string": "some string",
            "int": 1,
            "tuple": (1, 2, 3),
            # Set are not supported at the moment
            # "set": {1, 2, 3},
            "float": 1.1,
            "none": None,
        },
    )
    # Receive the message
    received = await sub.next_message()
    # Validate message subject
    assert received.subject == "testsub_data"
    # Validate message data
    assert received.data["string"] == "some string"
    assert received.data["int"] == 1
    assert received.data["tuple"] == [1, 2, 3]
    # assert received.data["set"] == [1, 2, 3]
    assert received.data["float"] == 1.1
    assert received.data["none"] is None


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_request_empty(broker: Broker) -> None:
    # Declare a subscription
    @broker.on_message("testsub_reply")
    async def cb(msg: Message):
        return {}

    # Start the subscription
    await broker.start()
    # Starting again should not cause an error
    await broker.start()
    # Request some reply
    result = await broker.request("testsub_reply")
    # Expect an empty dict as result
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_request_bad_message(broker: Broker) -> None:
    # Declare a subscription
    @broker.on_message("testsub_reply")
    async def cb(msg: Message):
        return True

    # Start the subscription
    await broker.start()
    # Starting again should not cause an error
    await broker.start()
    # Request some reply.
    # We expect to fail because the subscripton returns a boolean and not a JSONData
    with pytest.raises(InvalidMessageDataError):
        await broker.request("testsub_reply", timeout=0.5)


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_reply_empty(broker: Broker) -> None:
    # Declare a subscription
    @broker.on_message("testsub_reply")
    async def cb(msg: Message):
        return None

    # Start the subscription
    await broker.start()
    # Starting again should not cause an error
    await broker.start()
    # Request some reply
    result = await broker.request("testsub_reply")
    # Expect an empty dict as result
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_request_list(broker: Broker) -> None:
    """A list should not be treated as None."""
    # Define a subscription callback
    async def cb(msg: Message):
        return msg.data

    # Start subscription at same time
    await broker.subscribe("testsub_reply_list", cb=cb)
    # Perform a request
    result = await broker.request("testsub_reply_list", [])
    # Expect an empty list as result
    assert result == []


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_sync_subscription_callback(broker: Broker) -> None:
    """Synchronous callbacks should work just fine."""
    # Define a subscription with a sync callback (you should never do that)
    @broker.on_message("test_sync_callback")
    def on_message(msg: Message):
        return msg.data

    # Start broker
    await broker.start()
    # Perform a request
    reply = await broker.request("test_sync_callback", [1])
    # Validate reply
    assert reply == [1]


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_error_in_callback(broker: Broker) -> None:
    """Synchronous callbacks should work just fine."""
    # Define a subscription with a sync callback (you should never do that)
    @broker.on_message("test_sync_callback")
    def on_message(msg: Message):
        raise Exception("BOOM")

    # Start broker
    await broker.start()
    # Reply should never be received
    with pytest.raises(TimeoutError):
        await broker.request("test_sync_callback", [1])


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_subscribe_dependencies(broker) -> None:
    """A list should not be treated as None."""
    # Define some data model
    class Event(JsonModel):
        foo: List[str]

    # Create a callback
    async def cb(msg: Message, subject: Subject, event: Event):
        return msg.data

    # Start subscription
    sub = await broker.subscribe("testsub_reply_list", cb=cb)
    # Assert queue methods cannot be used
    with pytest.raises(Exception):
        await sub.listener(Message(subject="test", data={}))
    with pytest.raises(Exception):
        await sub.next_message()
    with pytest.raises(Exception):
        await sub.add_queue("test")
    # Make request
    result = await broker.request("testsub_reply_list", {"foo": []})
    # Ensure data did not change
    assert result["foo"] == []
    # Stop subscription
    await sub.stop()


@pytest.mark.asyncio
@pytest.mark.brokers
async def test_missing_dep(broker) -> None:
    # Create a model
    class Event(JsonModel):
        foo: List[str]

    # Create a callback
    async def cb(msg: Message, subject: Subject, event: Event, bad: 1):
        return msg.data

    # Start subscription
    sub = await broker.subscribe("testsub_reply_list", cb=cb)
    # Make request
    with pytest.raises(TimeoutError):
        await broker.request("testsub_reply_list", {"foo": []})

    await sub.stop()
