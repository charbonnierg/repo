import pytest
from quara.api import Storage


@pytest.fixture
async def storage() -> Storage:
    async with Storage("azure") as _storage:
        yield _storage
