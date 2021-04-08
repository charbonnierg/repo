from fastapi import FastAPI
from quara.api import Broker, Database, Scheduler, Storage
from quara.context import broker, database, scheduler, storage

# from quara.cu.client import ControlUnitClient


class BaseAPIMixin:
    _api: FastAPI


class LifeCycleMixin(BaseAPIMixin):
    @property
    def on_event(self):  # type: ignore[no-untyped-def]
        return self._api.on_event

    @property
    def middleware(self):  # type: ignore[no-untyped-def]
        return self._api.middleware

    @property
    def __call__(self):  # type: ignore[no-untyped-def]
        return self._api.__call__


class ApiMixin(BaseAPIMixin):
    @property
    def openapi(self):  # type: ignore[no-untyped-def]
        return self._api.openapi

    @property
    def router(self):  # type: ignore[no-untyped-def]
        return self._api.router

    @property
    def get(self):  # type: ignore[no-untyped-def]
        return self._api.get

    @property
    def post(self):  # type: ignore[no-untyped-def]
        return self._api.post

    @property
    def put(self):  # type: ignore[no-untyped-def]
        return self._api.put

    @property
    def patch(self):  # type: ignore[no-untyped-def]
        return self._api.patch

    @property
    def delete(self):  # type: ignore[no-untyped-def]
        return self._api.delete

    @property
    def options(self):  # type: ignore[no-untyped-def]
        return self._api.options

    @property
    def head(self):  # type: ignore[no-untyped-def]
        return self._api.head

    @property
    def trace(self):  # type: ignore[no-untyped-def]
        return self._api.trace

    @property
    def include_router(self):  # type: ignore[no-untyped-def]
        return self._api.include_router


class WebsocketMixin(BaseAPIMixin):
    @property
    def websocket(self):  # type: ignore[no-untyped-def]
        return self._api.websocket


class BrokerMixin:
    @property
    def broker(self) -> Broker:
        return broker.get()

    @property
    def on_message(self):  # type: ignore[no-untyped-def]
        return self.broker.on_message


class SchedulerMixin:
    @property
    def scheduler(self) -> Scheduler:
        return scheduler.get()

    @property
    def on_interval(self):  # type: ignore[no-untyped-def]
        return self.scheduler.on_interval


class StorageMixin:
    @property
    def objects(self) -> Storage:
        return storage.get()


class DatabaseMixin:
    @property
    def db(self) -> Database:
        return database.get()


# class InferenceMixin:
#     @property
#     def inference(self) -> Database:
#         return inference_engine.get()


# class ControlUnitMixin(StorageMixin, DatabaseMixin, InferenceMixin, BrokerMixin):
#     @property
#     def cu(self) -> ControlUnitClient:
#         return ControlUnitClient(
#             storage=self.objects,
#             database=self.db,
#             broker=self.broker,
#             inference=self.inference,
#         )
