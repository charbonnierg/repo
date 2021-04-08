# type: ignore[no-untyped-def]
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from quara.api import Message
from quara.core.errors import NoSuchBucketError
from quara.core.types import Json
from quara.services import Request, Service, ServiceRouter, WebSocket
from quara.services.utils import QueryFilters


@pytest.fixture
def service():  # noqa: C901
    app = Service()
    router = ServiceRouter()

    @router.get("/custom")
    async def custom_router():
        return {"status": "ok"}

    app.include_router(router)

    started = False
    tasks_ran = 0
    received = 0
    sent = 0

    @app.on_event("startup")
    def on_startup():
        nonlocal started
        started = True

    @app.middleware("http")
    async def increase_request_count(request: Request, call_next):
        nonlocal received
        nonlocal sent
        received += 1
        response = await call_next(request)
        sent += 1
        return response

    @app.on_message("subscribe-from-app")
    async def subscription_callback(msg: Message) -> Json:
        return {"status": "ok"}

    @app.on_interval(seconds=1)
    async def scheduler_callback() -> None:
        nonlocal tasks_ran
        tasks_ran += 1

    @app.get("/")
    def get():
        return {"status": "ok"}

    @app.post("/")
    def post():
        return {"status": "ok"}

    @app.patch("/")
    def patch():
        return {"status": "ok"}

    @app.put("/")
    def put():
        return {"status": "ok"}

    @app.delete("/")
    def delete():
        return {"status": "ok"}

    @app.options("/")
    def options():
        return {"status": "ok"}

    @app.head("/")
    def head():
        return {"status": "ok"}

    @app.trace("/")
    def trace():
        return {"status": "ok"}

    @app.post("/publish")
    async def publish():
        await app.broker.publish("publish-from-app", {"status": "ok"})
        return {"status": "ok"}

    @app.get("/query")
    async def query(filters: Dict[str, Any] = QueryFilters):
        col = app.db["count-from-app"]
        await col.delete_many()
        return await col.read_many_by_attr(**filters)

    @app.get("/count")
    async def count():
        col = app.db["count-from-app"]
        await col.delete_many()
        return {"count": await col.count()}

    @app.get("/objects")
    async def objects():
        try:
            await app.objects.delete_bucket("storage-from-app")
        except NoSuchBucketError:
            pass
        bucket = await app.objects.create_bucket("storage-from-app")
        return await bucket.list_objects()

    @app.websocket("/ws")
    async def on_websocket(websocket: WebSocket):
        await websocket.accept()
        await websocket.close()

    assert app.openapi is not None
    assert app.router.broker is not None
    assert app.router.db is not None
    assert app.router.objects is not None
    assert app.router.scheduler is not None

    return app


@pytest.fixture
async def client(service):
    # The test client is used to start events
    with TestClient(service):
        # QUARA HTTP client is used to perform requests
        async with AsyncClient(base_url="http://test", app=service) as _client:
            # It will close connections automatically after test
            _client.__app__ = service
            yield _client


@pytest.fixture
def test_files_directory() -> Path:
    return Path(__file__).parent / "test_files"
