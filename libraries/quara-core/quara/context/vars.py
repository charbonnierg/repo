from contextvars import ContextVar

from quara.api import Broker, Database, Scheduler, Storage

broker: ContextVar[Broker] = ContextVar("broker", default=None)
storage: ContextVar[Storage] = ContextVar("storage", default=None)
database: ContextVar[Database] = ContextVar("database", default=None)
scheduler: ContextVar[Scheduler] = ContextVar("scheduler", default=None)
