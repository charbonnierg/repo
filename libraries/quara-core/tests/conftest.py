from pathlib import Path

from faker import Faker
from pytest import fixture
from quara.api import AsyncExecutor, Broker, Database, Scheduler, Storage


@fixture
def test_files_directory() -> Path:
    """Path of test files directory."""
    return Path(__file__).parent / "test_files"


@fixture
def faker() -> Faker:
    """A faker instance."""
    return Faker()


@fixture
async def executor() -> AsyncExecutor:
    """A test executor."""
    return AsyncExecutor()


@fixture
async def broker() -> Broker:
    """A test broker."""
    async with Broker.from_context() as _broker:
        yield _broker


@fixture
async def database() -> Database:
    """A test database."""
    async with Database.from_context() as db:
        yield db


@fixture
async def storage() -> Storage:
    async with Storage.from_context() as _storage:
        yield _storage


@fixture
async def scheduler() -> Scheduler:
    yield Scheduler.from_context()
