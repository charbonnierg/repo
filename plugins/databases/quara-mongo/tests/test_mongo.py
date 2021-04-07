# type: ignore[no-untyped-def]
import pytest
from quara.api import Database


@pytest.mark.asyncio
@pytest.mark.mongo
async def test_lazy_connect():
    db = Database("mongo")
    await db.connect(lazy=True)
    # Try to iterate on collection
    async for document in db["test-lazy-connect"].iterate_many(limit=0):
        break
