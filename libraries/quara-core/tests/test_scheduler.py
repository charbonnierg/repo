import asyncio

import pytest
from quara.api import Scheduler


@pytest.mark.asyncio
@pytest.mark.schedulers
async def test_scheduler(scheduler: Scheduler):

    v = 0

    @scheduler.on_interval(seconds=1)
    async def test_task():
        nonlocal v
        v += 1

    await scheduler.start()
    # Starting multiple times should not raise an error
    await scheduler.start()
    await asyncio.sleep(1)
    await scheduler.stop(force=True)
    await asyncio.sleep(1)
    assert v == 1
    for task in scheduler._backend._schedules:
        # Starting a task already running should not raise an error
        await task.start()
    # Check that s
    # Stop the scheduler
    await scheduler.stop()
    # Stopping multiple times should not raise an error
    await scheduler.stop()
