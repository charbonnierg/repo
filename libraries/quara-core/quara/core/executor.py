from asyncio import get_event_loop
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T", bound=Any)


class AsyncExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers: Optional[int] = 4, **kwargs: Any) -> None:
        """Create a new instance of Async executor."""
        super().__init__(max_workers=max_workers, **kwargs)

    async def run(self, func: Callable[..., T], /, *args: Any, **kwargs: Any) -> T:
        """Run a function in the current event loop using the instance thread pool executor.

        Examples:

        ```python
        def blocking(x: int, y: int) -> int:
            return x + y

        async def foo(x: int, y: int) -> int
            return await run_async(blocking, x, y=y)
        ```
        """
        # TODO: How to make sure that we can get the same event loop at instance creation ?
        _loop = get_event_loop()
        _func = partial(func, *args, **kwargs)
        return await _loop.run_in_executor(self, _func)
