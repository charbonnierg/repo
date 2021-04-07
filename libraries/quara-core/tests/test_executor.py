# type: ignore[no-redef]
import pytest


@pytest.mark.asyncio
@pytest.mark.core
async def test_async_executor(executor):
    def func():
        pass

    result = await executor.run(func)
    assert result is None

    def func():
        return 1

    result = await executor.run(func)
    assert result == 1

    def func(x: int, /, y: float):
        return x / y

    result = await executor.run(func, 0, 1)
    assert result == 0

    result = await executor.run(func, 0, y=1)
    assert result == 0

    def func(x: int, y: float, **kwargs):
        return x + y + kwargs.get("test")

    result = await executor.run(func, 0, y=1, test=2)
    assert result == 3
