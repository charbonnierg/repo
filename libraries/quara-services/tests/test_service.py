# type: ignore[no-untyped-def]
import nest_asyncio
import pytest
from httpx import AsyncClient
from quara.services import Service

nest_asyncio.apply()


@pytest.mark.asyncio
@pytest.mark.services
async def test_endpoints(client: AsyncClient):
    app: Service = client.__app__

    assert app.broker._connected

    res = await client.get("/custom")
    assert res.json() == {"status": "ok"}

    res = await client.get("/")
    assert res.json() == {"status": "ok"}

    res = await client.post("/")
    assert res.json() == {"status": "ok"}

    res = await client.patch("/")
    assert res.json() == {"status": "ok"}

    res = await client.put("/")
    assert res.json() == {"status": "ok"}

    res = await client.delete("/")
    assert res.json() == {"status": "ok"}

    res = await app.broker.request("subscribe-from-app")
    assert res == {"status": "ok"}

    sub = await app.broker.subscribe("publish-from-app")
    res = await client.post("/publish")
    assert res.json() == {"status": "ok"}
    msg = await sub.next_message(1)
    assert msg.data == {"status": "ok"}

    res = await client.get("/count")
    assert res.json() == {"count": 0}

    res = await client.get("/query")
    assert res.json() == []

    res = await client.get("/query", params={"a": 1})
    # Query parameters are always string by default
    assert res.json() == []

    res = await client.get("/query", params={"from_date": "2020-01-01T00:00:00"})
    # Query parameters are always string by default
    assert res.json() == []

    # res = await client.get("/objects")
    # assert res.json() == []
