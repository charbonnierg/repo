from __future__ import annotations

from datetime import datetime, tzinfo
from typing import Any, Callable, Coroutine, Dict, Optional, Union

from quara.api.schedulers.context import SchedulerContext
from quara.core.plugins import Pluggable

from .backend import SchedulerBackend
from .task import ScheduledTask


class Scheduler(Pluggable[SchedulerBackend]):

    __group__ = "quara.schedulers"
    __default_backend__ = "apscheduler"

    def __init__(self, backend: Optional[str] = None, /, **kwargs: Any) -> None:
        """Create a new instance of Message Broker.

        By default "nats" backend is used.

        Arguments:
            backend: The backend implementation to use.
            kwargs: Additional keyword arguments forwarded to backend as options.

        Returns:
            None
        """
        super().__init__(backend, **kwargs)
        self._connected = False

    async def start(self, **kwargs: Any) -> None:
        if not self._connected:
            await self._backend.start()
            self._connected = True

    async def stop(self, force: bool = False, **kwargs: Any) -> None:
        if self._connected:
            await self._backend.stop(force=force)
            self._connected = False

    @classmethod
    def from_context(
        cls, context: Union[SchedulerContext, Dict[str, Any], None] = None
    ) -> Scheduler:
        """Create a new database from context."""
        if context:
            if isinstance(context, SchedulerContext):
                options = context.dict(exclude_unset=True)
            else:
                options = context
        else:
            options = {}
        options.pop("enabled", None)
        return cls(**options)

    def on_interval(
        self,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        seconds: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        timezone: Optional[tzinfo] = None,
        jitter: Optional[int] = None,
    ) -> Callable[
        [Callable[..., Coroutine[None, None, None]]],
        Callable[..., Coroutine[None, None, None]],
    ]:
        """Decorate a function to be used as scheduler task."""
        # on_schedule is a decorator that accepts decorator arguments and not the decorated function
        # the function below accepts the decorated function as argument
        def schedule_factory(
            cb: Callable[..., Coroutine[None, None, None]]
        ) -> Callable[..., Coroutine[None, None, None]]:
            """Create a subscription factory from a given callback."""
            # Create subscription
            schedule = ScheduledTask(
                self._backend,
                cb,
                weeks=weeks,
                days=days,
                hours=hours,
                seconds=seconds,
                start_date=start_date,
                end_date=end_date,
                timezone=timezone,
                jitter=jitter,
            )
            # Store schedule on backend
            self._backend._schedules.append(schedule)
            # Return function so that python does not complain
            # Note: The return value is never used
            return cb

        # Return subscription_factory which will act as decorator
        return schedule_factory


__all__ = ["Scheduler"]
