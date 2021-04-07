from __future__ import annotations

from datetime import datetime, tzinfo
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .backend import SchedulerBackend


class ScheduledTask:
    def __init__(
        self,
        backend: SchedulerBackend,
        /,
        task: Callable[..., Any],
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        seconds: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        timezone: Optional[tzinfo] = None,
        jitter: Optional[int] = None,
    ) -> None:
        self._backend = backend
        self._started = False
        self.scheduled_id: Optional[str] = None
        self.task = task
        self.task_interval_specs = dict(
            weeks=weeks,
            days=days,
            hours=hours,
            seconds=seconds,
            start_date=start_date,
            end_date=end_date,
            timezone=timezone,
            jitter=jitter,
        )

    async def start(self, **kwargs: Any) -> None:
        if not self._started:
            self.scheduled_id = await self._backend.add_task(self, **kwargs)
            self._started = True


__all__ = ["ScheduledTask"]
