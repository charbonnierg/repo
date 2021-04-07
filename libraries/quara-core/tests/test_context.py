# type: ignore[attr-defined]
import json
from pathlib import Path

import pytest
from quara.api import Broker, Database, Scheduler, Storage
from quara.context import (
    BrokerContext,
    Context,
    DatabaseContext,
    StorageContext,
    broker,
    database,
    scheduler,
    storage,
)


@pytest.mark.services
def test_default_context():
    c = Context()
    # Validate default broker context
    default_broker_context = BrokerContext()
    assert c.broker.backend == default_broker_context.backend
    assert c.broker.host == default_broker_context.host
    assert c.broker.port == default_broker_context.port
    assert c.broker.tls == default_broker_context.tls
    assert c.broker.servers is None
    # Validate default database context
    default_database_context = DatabaseContext()
    assert c.database.backend == default_database_context.backend
    assert c.database.host == default_database_context.host
    assert c.database.port == default_database_context.port
    assert c.database.name == default_database_context.name
    assert c.database.timeout == default_database_context.timeout
    # Validate storage context
    default_storage_context = StorageContext()
    assert c.storage.backend == default_storage_context.backend
    assert c.storage.host == default_storage_context.host
    assert c.storage.port == default_storage_context.port
    assert c.storage.access_key == default_storage_context.access_key
    assert c.storage.secret_key == default_storage_context.secret_key
    assert c.storage.secure == default_storage_context.secure
    # Assert that dict access is working
    assert c["storage"]["backend"] == default_storage_context.backend
    assert c.get("storage").get("backend") == default_storage_context.backend
    c.update(storage={"backend": "custom"})
    assert c.storage.backend == "custom"
    assert c.storage.host == default_storage_context.host


@pytest.mark.services
def test_context_storage_property():
    c = Context()
    c.storage = {"port": 8000}
    c.storage = {"host": "127.0.0.1"}
    assert c.storage.host == "127.0.0.1"
    assert c.storage.port == Context().storage.port
    with pytest.raises(Exception):
        c.storage = {"host": [1, 2, 3]}


@pytest.mark.services
def test_context_database_property():
    c = Context()
    c.database = {"port": 8000}
    c.database = {"host": "127.0.0.1"}
    assert c.database.host == "127.0.0.1"
    assert c.database.port == Context().database.port
    with pytest.raises(Exception):
        c.database = {"host": [1, 2, 3]}


@pytest.mark.services
def test_context_broker_property():
    c = Context()
    c.broker = {"port": 8000}
    c.broker = {"host": "127.0.0.1"}
    assert c.broker.host == "127.0.0.1"
    assert c.broker.port == Context().broker.port
    with pytest.raises(Exception):
        c.broker = {"host": [1, 2, 3]}


@pytest.mark.services
def test_context_repr():
    c = Context()
    assert repr(c) == json.dumps(c.dict(), indent=2)


@pytest.mark.services
def test_context_from_file(test_files_directory: Path):
    c = Context(path=test_files_directory / "test.yml")
    assert c.get("extra_options").get("name") == "test"
    assert c.broker.host == "127.0.0.1"


@pytest.mark.services
def test_priorities():
    c = Context({"broker": {"host": "A"}}, broker={"host": "B"})
    assert c.broker.host == "B"


@pytest.mark.services
def test_contextvars_disabled():
    c = Context(
        broker=dict(enabled=False),
        database=dict(enabled=False),
        storage=dict(enabled=False),
        scheduler=dict(enabled=False),
    )
    assert not c.broker.enabled
    assert not c.database.enabled
    assert not c.storage.enabled
    assert not c.scheduler.enabled
    # Set contextvars
    c.set_contextvars()
    # Ensure scheduler has been instantiated
    _s: Scheduler = scheduler.get()
    assert _s is None
    # Ensure database has been instantiated
    _db: Database = database.get()
    assert _db is None
    # Ensure broker has been instantiated
    _b: Broker = broker.get()
    assert _b is None
    # Ensure storage has been instantiated
    _s: Storage = storage.get()
    assert _s is None


@pytest.mark.services
def test_contextvars():
    c = Context()
    c.set_contextvars()
    # Ensure scheduler has been instantiated
    _s: Scheduler = scheduler.get()
    assert _s is not None
    # Ensure database has been instantiated
    _db: Database = database.get()
    assert _db is not None
    assert not _db._connected
    # Ensure broker has been instantiated
    _b: Broker = broker.get()
    assert _b is not None
    assert not _b._connected
    # Ensure storage has been instantiated
    _s: Storage = storage.get()
    assert _s is not None
