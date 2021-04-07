# Backports for python <= 3.8
from __future__ import annotations

# Standard library import
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, AsyncIterator, Dict, List, Optional

# MongoDB related imports
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import errors as _errors
from pymongo.client_session import ClientSession
from quara.api.databases import (
    DatabaseBackend,
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
)
from quara.core.errors import DatabaseError

from .utils import (
    dict_to_document,
    generate_filters,
    map_dict_to_documents,
    sanitize_document_id,
)


class MongoError(DatabaseError):
    def __init__(self, msg: str, err: Exception):
        self.msg = msg
        self.err = err


class AsyncioMongoDatabase(DatabaseBackend):
    """A Motor implementation of documents collection client."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 27017,
        name: str = "quara",
        timeout: int = 30,
        **kwargs: Any,
    ):
        """Create a new instance of AsyncioMongoDatabase."""
        self.host = host
        self.port = port
        self.name = name
        self.timeout = timeout
        self._motor_options = kwargs

    async def connect(self, lazy: bool = False) -> None:
        """Establish connection with the MongoDB database."""
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(
            self.host, self.port, **self._motor_options
        )
        self.db: AsyncIOMotorDatabase = self.client[self.name]
        # Ping the server to make sure connection is alive
        if not lazy:
            await self.db.command("ping")

    async def close(self) -> None:
        """Close connection to the database."""
        self.client.close()

    async def iterate_many(
        self,
        collection: str,
        /,
        filter: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
        *,
        limit: int = 1000,
        offset: int = 0,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Asynchronously yields documents matching filter from a collection."""
        if not hasattr(self, "db"):
            raise Exception("Database client is not connected")
        # MongoDB use an empty dict to denote that no filter is used
        filter = filter or {}
        # Prepare filter
        if filter:
            filter = generate_filters(**filter)
        # Prepare projections
        if projection and "id" in projection:
            projection["_id"] = projection.pop("id")
        # Get a cursor
        try:
            cursor = self.db[collection].find(
                filter, projection, session=session, **kwargs
            )
        # Catch any error that might occur during cursor creation
        except _errors.PyMongoError as err:
            raise MongoError(
                "Failed to iterate over collection.",
                err,
            )
        # Apply limit to cursor
        if limit:
            cursor.limit(int(limit))
        # Apply offset to cursor
        if offset:
            cursor.skip(int(offset))
        # Iterate cursor and sanizatize documents
        async for result in cursor:
            yield sanitize_document_id(result)

    async def count(
        self,
        /,
        collection: str,
        *,
        filter: Optional[Dict[str, Any]] = None,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> int:
        """Count number of documents in collection. Optionally accept a filter argument."""
        if not hasattr(self, "db"):
            raise Exception("Database client is not connected")
        # MongoDB use an empty dict to denote that no filter is used
        filter = filter or {}
        try:
            count: int = await self.db[collection].count_documents(
                filter, session=session, **kwargs
            )
        except _errors.PyMongoError as error:
            raise MongoError("Failed to count collection documents", error)
        return count

    async def create_one(
        self,
        collection: str,
        /,
        document: Dict[str, Any],
        *,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> InsertOneResult:
        """Create a single document into a collection."""
        if not hasattr(self, "db"):
            raise Exception("Database client is not connected")
        try:
            # As MongoDB mutates the inserted dictionary with the updated _id, we need to copy it.
            result = await self.db[collection].insert_one(
                dict_to_document(document), session=session, **kwargs
            )
        except _errors.PyMongoError as error:
            raise MongoError("Failed to create document", error)
        return InsertOneResult(inserted_id=str(result.inserted_id))

    async def create_many(
        self,
        collection: str,
        /,
        documents: List[Dict[str, Any]],
        *,
        session: Optional[Any] = None,
        # Use ordered = True to allow inserts to continue on DuplicateKeyError
        ordered: bool = False,
        **kwargs: Any,
    ) -> InsertManyResult:
        """Create many documents into a collection."""
        if not hasattr(self, "db"):
            raise Exception("Database client is not connected")
        try:
            # As MongoDB mutates the inserted dictionaries with the updated _id, we need to copy them.
            result = await self.db[collection].insert_many(
                map_dict_to_documents(documents),
                session=session,
                ordered=ordered,
            )
        except _errors.PyMongoError as error:
            raise MongoError("Failed to create many documents", error)
        return InsertManyResult(inserted_ids=[str(_id) for _id in result.inserted_ids])

    async def delete_many(
        self,
        /,
        collection: str,
        *,
        filter: Optional[Dict[str, Any]] = None,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> DeleteResult:
        """Delete many documents."""
        if not hasattr(self, "db"):
            raise Exception("Database client is not connected")
        # When no filter is used, whole collection is deleted
        filter = filter or {}
        # Prepare filters
        filter = generate_filters(**filter)
        # Execute query
        try:
            result = await self.db[collection].delete_many(
                filter, session=session, **kwargs
            )
        except _errors.PyMongoError as error:
            raise MongoError("Failed to delete many documents", error)
        return DeleteResult(deleted_count=result.deleted_count)

    async def delete_one(
        self,
        /,
        collection: str,
        *,
        filter: Optional[Dict[str, Any]] = None,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> DeleteResult:
        """Delete one document from collection."""
        if not hasattr(self, "db"):
            raise Exception("Database client is not connected")
        # When no filter is used, whole collection is deleted
        filter = filter or {}
        # Prepare filters
        filter = generate_filters(**filter)
        # Execute query
        try:
            result = await self.db[collection].delete_one(
                filter, session=session, **kwargs
            )
        except _errors.PyMongoError as error:
            raise MongoError("Failed to delete one document", error)
        return DeleteResult(deleted_count=result.deleted_count)

    async def update_many(
        self,
        collection: str,
        /,
        update_document: Dict[str, Any],
        *,
        filter: Optional[Dict[str, Any]] = None,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> UpdateResult:
        """Update many documents."""
        if not hasattr(self, "db"):
            raise Exception("Database client is not connected")
        # When no filter is used, whole collection is deleted
        filter = filter or {}
        # Prepare filters
        filter = generate_filters(**filter)
        # Execute query
        try:
            result = await self.db[collection].update_many(
                filter, {"$set": update_document}, session=session, **kwargs
            )
        except _errors.PyMongoError as error:
            raise MongoError("Failed to update many documents", error)
        return UpdateResult(modified_count=result.matched_count)

    async def update_one(
        self,
        collection: str,
        /,
        update_document: Dict[str, Any],
        *,
        filter: Optional[Dict[str, Any]] = None,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> UpdateResult:
        """Update one document from collection.

        Arguments:
            collection: The collection to query.
            update_document: The data to update in the documents as a dictionary.
            filter: The filter used to query document to update.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An update result.
        """
        if not hasattr(self, "db"):
            raise Exception("Database client is not connected")
        # When no filter is used, whole collection is deleted
        filter = filter or {}
        # Prepare filters
        filter = generate_filters(**filter)
        # Execute query
        try:
            result = await self.db[collection].update_one(
                filter, {"$set": update_document}, session=session, **kwargs
            )
        except _errors.PyMongoError as error:
            raise MongoError("Failed to update one document", error)
        return UpdateResult(modified_count=result.matched_count)

    @asynccontextmanager
    async def start_transaction(self) -> AsyncIterator[ClientSession]:
        """Start a transaction using an async context manager."""
        if not hasattr(self, "db"):
            raise Exception("Database client is not connected")
        # First start session
        async with await self.client.start_session() as s:
            # Then start transaction
            async with s.start_transaction():
                # Yield the instance
                yield s

    async def destroy(self) -> None:
        for db in await self.client.list_database_names():
            if db in ("admin", "config", "local"):
                continue
            self.client.drop_database(db)
