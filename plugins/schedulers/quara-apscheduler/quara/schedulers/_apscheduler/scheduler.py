from __future__ import annotations

from typing import Any, List

# Apscheduler related imports
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from quara.api.schedulers import ScheduledTask


class AsyncioScheduler:
    def __init__(self, **kwargs: Any) -> None:
        """Create a new instance of AsyncioScheduler."""
        self._scheduler = AsyncIOScheduler()
        self._schedules: List[ScheduledTask] = []

    async def start(self) -> None:
        for task in self._schedules:
            await task.start()
        self._scheduler.start()

    async def stop(self, force: bool = False) -> None:
        self._scheduler.shutdown(force)

    async def add_task(self, task: ScheduledTask, **kwargs: Any) -> None:
        trigger = IntervalTrigger(**task.task_interval_specs)
        self._scheduler.add_job(task.task, trigger, **kwargs)
