from typing import AsyncGenerator

from pytest import fixture
from quara.api import Broker


@fixture
async def broker() -> AsyncGenerator[Broker, None]:
    async with Broker("nats") as broker:
        assert broker._connected
        yield broker
