from __future__ import annotations

from typing import Any

from quara.context import Context

from .errors import add_catch_exceptions_middleware
from .mixins import (
    ApiMixin,
    BrokerMixin,
    DatabaseMixin,
    LifeCycleMixin,
    SchedulerMixin,
    StorageMixin,
    WebsocketMixin,
)
from .routing import fastapi


class Service(
    ApiMixin,
    BrokerMixin,
    DatabaseMixin,
    StorageMixin,
    LifeCycleMixin,
    SchedulerMixin,
    WebsocketMixin,
):
    def __init__(self, context: Context = Context(), **kwargs: Any) -> None:
        self._api = fastapi.applications.FastAPI(**kwargs)
        self.context = context
        self.context.set_contextvars()
        self.on_event("startup")(self._start_resources)
        self.on_event("shutdown")(self._stop_resources)
        add_catch_exceptions_middleware(self._api)

    async def _start_resources(self) -> None:
        """Start all resources."""
        if self.context.broker.enabled:
            await self.broker.start()
        if self.context.scheduler.enabled:
            await self.scheduler.start()
        if self.context.database.enabled:
            await self.db.connect()

    async def _stop_resources(self) -> None:
        """Stop all resources."""
        if self.context.broker.enabled:
            await self.broker.close()
        if self.context.scheduler.enabled:
            await self.scheduler.stop()
        if self.context.database.enabled:
            await self.db.close()

    async def start(self) -> None:
        """Start the application.

        Should only be used in development !
        """
        import uvicorn

        await self._start_resources()
        uvicorn.run(self)
