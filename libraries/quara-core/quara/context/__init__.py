import json
from contextvars import ContextVar, Token
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

from quara.api import Broker, Database, Scheduler, Storage
from quara.api.brokers.context import BrokerContext
from quara.api.databases.context import DatabaseContext
from quara.api.schedulers.context import SchedulerContext
from quara.api.storages.context import StorageContext
from quara.core.dicts import deep_update, dict_from_yaml

broker: ContextVar[Broker] = ContextVar("broker", default=None)
storage: ContextVar[Storage] = ContextVar("storage", default=None)
database: ContextVar[Database] = ContextVar("database", default=None)
scheduler: ContextVar[Scheduler] = ContextVar("scheduler", default=None)


class Context:
    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        *,
        path: Optional[Union[Path, str]] = None,
        **kwargs: Any,
    ) -> None:
        # Initialize empty state
        self.data: Dict[str, Any] = {}
        # Load state from file
        if path:
            file_data = dict_from_yaml(path)
            self.update(file_data)
        # Override state with positional argument
        if data:
            self.update(data)
        # Override state with kwargs
        if kwargs:
            self.update(kwargs)
        # Do an update if it has not been done yet
        if not self.data:
            self.update()
        # Set tokens dictionnary
        self.tokens: Dict[str, Token[str]] = {}

    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, Any]:
        data = data.copy()
        broker = BrokerContext(**data.get("broker", {}))
        data["broker"] = broker.dict()
        database = DatabaseContext(**data.get("database", {}))
        data["database"] = database.dict()
        storage = StorageContext(**data.get("storage", {}))
        data["storage"] = storage.dict()
        scheduler = SchedulerContext(**data.get("scheduler", {}))
        data["scheduler"] = scheduler.dict()
        return data

    def update(self, other: Mapping[str, Any] = {}, /, **kwargs: Any) -> None:
        new_data = deep_update(self.data, other)
        new_data = deep_update(new_data, kwargs)
        self.data = self.validate(new_data)
        self._broker = BrokerContext.construct(**self.data["broker"])
        self._database = DatabaseContext.construct(**self.data["database"])
        self._storage = StorageContext.construct(**self.data["storage"])
        self._scheduler = SchedulerContext.construct(**self.data["scheduler"])

    @property
    def broker(self) -> BrokerContext:
        return self._broker

    @broker.setter
    def broker(self, kwargs: Dict[str, Any]) -> None:
        self._broker = BrokerContext(**kwargs)
        self.data["broker"] = self._broker.dict()

    @property
    def database(self) -> DatabaseContext:
        return self._database

    @database.setter
    def database(self, kwargs: Dict[str, Any]) -> None:
        self._database = DatabaseContext(**kwargs)
        self.data["database"] = self._database.dict()

    @property
    def storage(self) -> StorageContext:
        return self._storage

    @storage.setter
    def storage(self, kwargs: Dict[str, Any]) -> None:
        self._storage = StorageContext(**kwargs)
        self.data["storage"] = self._storage.dict()

    @property
    def scheduler(self) -> SchedulerContext:
        return self._scheduler

    @scheduler.setter
    def scheduler(self, kwargs: Dict[str, Any]) -> None:
        self._scheduler = SchedulerContext(**kwargs)
        self.data["scheduler"] = self._scheduler.dict()

    def __getitem__(self, name: str) -> Dict[str, Any]:
        # mypy complains that type is Any
        return self.data[name]  # type: ignore

    def get(self, name: str, default: Optional[Any] = None) -> Dict[str, Any]:
        return self.data.get(name, default)

    def dict(self) -> Dict[str, Any]:
        return self.data

    def json(self, **kwargs: Any) -> str:
        return json.dumps(self.data, **kwargs)

    def __str__(self) -> str:
        return self.json(indent=0)

    def __repr__(self) -> str:
        output = self.data
        output["storage"]["secret_key"] = 7 * "*"
        return json.dumps(output, indent=2)

    def set_contextvars(self) -> None:

        options = self.database.dict()
        enabled = options.pop("enabled")
        if enabled:
            backend = options.pop("backend")
            self.tokens["database"] = database.set(Database(backend, **options))

        options = self.broker.dict()
        enabled = options.pop("enabled")
        if enabled:
            backend = options.pop("backend")
            self.tokens["broker"] = broker.set(Broker(backend, **options))

        options = self.storage.dict()
        enabled = options.pop("enabled")
        if enabled:
            backend = options.pop("backend")
            self.tokens["storage"] = storage.set(Storage(backend, **options))

        options = self.scheduler.dict()
        enabled = options.pop("enabled")
        if enabled:
            backend = options.pop("backend")
            self.tokens["scheduler"] = scheduler.set(Scheduler(backend, **options))

    def get_db(self) -> Database:
        return database.get()

    def get_broker(self) -> Broker:
        return broker.get()

    def get_storage(self) -> Storage:
        return storage.get()
