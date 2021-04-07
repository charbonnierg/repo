from __future__ import annotations

from abc import abstractmethod
from typing import Any, List  # , Awaitable, Callable, Optional

from quara.core.plugins import Plugin

from .task import ScheduledTask


class SchedulerBackend(Plugin):
    _scheduler: Any
    _schedules: List[ScheduledTask]

    @abstractmethod
    def __init__(self, **kwargs: Any) -> None:
        """Create a new instance of Scheduler backend.

        Arguments:
            kwargs: Additional keyword arguments forwarded to backend as options.

        Returns:
            None
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def start(self, **kwargs: Any) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def stop(self, force: bool = False, **kwargs: Any) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def add_task(self, task: ScheduledTask, **kwargs: Any) -> Any:
        raise NotImplementedError  # pragma: no cover


__all__ = ["SchedulerBackend"]
