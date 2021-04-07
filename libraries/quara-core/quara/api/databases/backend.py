from __future__ import annotations

from abc import abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager, AsyncGenerator, Dict, List, Optional

from quara.core.plugins import Plugin

from .defaults import (
    DEFAULT_FILTER,
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    DEFAULT_PROJECTION,
    DEFAULT_SESSION,
)
from .results import DeleteResult, InsertManyResult, InsertOneResult, UpdateResult


class DatabaseBackend(Plugin):
    """A base class for asynchronous database clients to operate CRUD operations on collections."""

    @abstractmethod
    def __init__(self, **kwargs: Any) -> None:
        """Create a new instance of DatabaseBackend.

        When possible, use "host", "port", and "database" keyword
        arguments to identify database server URI (it might not make sense
        in some cases, for example Azure CosmosDB).

        Arguments:
            kwargs: Additional arguments specific to backend.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def connect(self, **kwargs: Any) -> None:
        """Connect to the database.

        When possible, do not require arguments for the connect method.

        When working with databases that are lazy such as mongo
        always ensure connection is alive in the connect method by
        default.

        Arguments:
            kwargs: Additional arguments specific to backend.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def close(self, **kwargs: Any) -> None:
        """Close connection the database.

        When possible, do not require arguments for the close method.

        Arguments:
            kwargs: Additional arguments specified to backend.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def count(
        self,
        /,
        collection: str,
        *,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> int:
        """Count documents in a collection.

        Arguments:
            collection: The collection to query.
            filter: A valid pymongo filter to use when querying database.
            session: The session to use when using transactions.
            kwargs: Additional arguments specified to backend.

        Returns:
            The number of documents (optionally matching filter) in the collection.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def iterate_many(
        self,
        collection: str,
        /,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Iterate on some documents matching given filter from collection.

        Arguments:
            collection: The collection to query documents from.
            filter: Dictionary to filter documents to query.
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to fetch.
            offset: The offset from which start fetching documents.
            session: The session to use when using transactions.
            kwargs: Additional arguments specified to backend.

        Returns:
            An asynchronous generator that yields dictionnaries.
        """
        yield {}  # pragma: no cover
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def create_one(
        self,
        collection: str,
        /,
        document: Dict[str, Any],
        *,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> InsertOneResult:
        """Create one document in collection.

        Arguments:
            collection: The collection to query documents from.
            document: The document's content as a dictionary.
            session: The session to use when using transactions.
            kwargs: Additional arguments specified to backend.

        Returns:
            An insertion result.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def create_many(
        self,
        collection: str,
        /,
        documents: List[Dict[str, Any]],
        *,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> InsertManyResult:
        """Create many documents in collection.

        Arguments:
            collection: The collection to query.
            documents: The list of document's content as dictionaries.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A many insert result.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def delete_many(
        self,
        /,
        collection: str,
        *,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> DeleteResult:
        """Delete many documents from collection.

        An empty filter means that all documents from collection should be removed.

        Arguments:
            collection: The collection to query.
            filter: Dictionary to filter documents to delete.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A delete result.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def delete_one(
        self,
        /,
        collection: str,
        *,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> DeleteResult:
        """Delete one document from collection.

        An empty filter means that the first document found in collection should be removed.

        Arguments:
            collection: The collection to query.
            filter: Dictionary to filter documents to delete.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A delete result.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def update_many(
        self,
        collection: str,
        /,
        update_document: Dict[str, Any],
        *,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> UpdateResult:
        """Update many documents from collection.

        Arguments:
            collection: The collection to query.
            update_document: The data to update in the documents as a dictionary.
            filter: The filter used to query documents to update.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An update result.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def update_one(
        self,
        collection: str,
        /,
        update_document: Dict[str, Any],
        *,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        session: Optional[Any] = DEFAULT_SESSION,
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
        raise NotImplementedError  # pragma: no cover

    @asynccontextmanager  # type: ignore
    async def start_transaction(
        self, *args: Any, **kwargs: Any
    ) -> AsyncContextManager[Any]:
        """It is not mandatory to implement the start_transaction method."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def destroy(self) -> None:
        """Destroy the whole database."""
        raise NotImplementedError  # pragma: no cover


__all__ = ["DatabaseBackend"]
