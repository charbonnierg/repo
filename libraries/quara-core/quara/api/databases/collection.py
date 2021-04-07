from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, List, Optional

from .defaults import (
    DEFAULT_FILTER,
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    DEFAULT_PROJECTION,
    DEFAULT_SESSION,
)
from .results import DeleteResult, InsertManyResult, InsertOneResult, UpdateResult

if TYPE_CHECKING:  # pragma: no cover
    from .client import Database


class Collection:
    def __init__(self, database: Database, name: str):
        """Return a new collection instance."""
        self._database = database
        self.name = name

    async def count(
        self,
        *,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> int:
        """Determine the number of documents in the collection.

        Arguments:
            collection: The collection to query.
            filter: A valid pymongo filter to use when querying database.
            session: The session to use when using transactions.
            kwargs: Additional arguments specified to backend.

        Returns:
            The number of documents (optionally matching filter) in the collection.
        """
        return await self._database.count(
            self.name, filter=filter, session=session, **kwargs
        )

    async def iterate_many(
        self,
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
            filter: Dictionary to filter documents to query.
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to fetch.
            offset: The offset from which start fetching documents.
            session: The session to use when using transactions.
            kwargs: Additional arguments specified to backend.

        Returns:
            An asynchronous generator that yields dictionnaries.

        ### References:

        * PEP 525 -- Asynchronous Generators: <https://www.python.org/dev/peps/pep-0525/>
        * `typing.AsyncGenerator` documentation: <https://docs.python.org/3/library/typing.html#typing.AsyncGenerator>
        """
        async for document in self._database.iterate_many(
            self.name,
            filter=filter,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        ):
            yield document

    async def read_many(
        self,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Read some documents from collection.

        Arguments:
            limit: The maximum documents of items to fetch.
            filter: The filter to apply as a dict.
            projection: Dictionary to filter documents fields to return.
            offset: The offset from which start fetching documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A list of documents as dictionaries.
        """
        return await self._database.read_many(
            self.name,
            filter=filter,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        )

    async def iterate_all(
        self,
        *,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Return an iterator on all documents from collection.

        Arguments:
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to iterate on.
            offset: The offset from which start iterating on documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An asynchronous generator yielding documents as dictionaries.
        """
        async for document in self._database.iterate_all(
            self.name,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        ):
            yield document

    async def read_all(
        self,
        *,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Read all documents from collection.

        Arguments:
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to fetch.
            offset: The offset from which start fetching documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A list of documents as dictionaries.
        """
        return await self._database.read_all(
            self.name,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        )

    async def iterate_many_by_id(
        self,
        ids: List[str],
        *,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Return an iterator on documents from collection by IDs.

        IDs that were not matching any document are not present in returned iterator.

        Arguments:
            ids: The IDs of the documents to iterate on.
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to iterate on.
            offset: The offset from which start iterating on documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An asynchronous generator yielding documents as dictionaries.
        """
        async for document in self._database.iterate_many_by_id(
            self.name,
            ids=ids,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        ):
            yield document

    async def iterate_many_by_attr(
        self,
        *,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Return an iterator on documents from collection by their attributes.

        Arguments:
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to iterate on.
            offset: The offset from which start iterating on documents.
            session: The session to use when using transactions.
            **kwargs: Arguments containing attributes defining filter.

        Returns:
            An asynchronous generator yielding documents as dictionaries.
        """
        async for document in self._database.iterate_many_by_attr(
            self.name,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        ):
            yield document

    async def read_many_by_id(
        self,
        ids: List[str],
        *,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Read many documents from collection by IDs.

        IDs that were not matching any document are not present in return list,
        thus the return list length might be smaller than the length of requested IDs list.

        Arguments:
            ids: The IDs of the documents to read.
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to fetch.
            offset: The offset from which start fetching documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A list of matching documents as dictionaries.
        """
        return await self._database.read_many_by_id(
            self.name,
            ids=ids,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        )

    async def read_many_by_attr(
        self,
        *,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Read many documents from collection by their attributes.

        Arguments:
            collection: The collection to query.
            limit: The maximum documents of items to fetch.
            offset: The offset from which start fetching documents.
            session: The session to use when using transactions.
            **kwargs: Arguments containing attributes defining filter.

        Returns:
            A list of documents as dictionaries.
        """
        return await self._database.read_many_by_attr(
            self.name,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        )

    async def read_one(
        self,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        *,
        offset: int = 0,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """Find the first document matching filter or return None.

        Arguments:
            filter: The filter to apply as a dict.
            projection: Dictionary to filter documents fields to return.
            offset: The offset from which start fetching documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            None or the document as dictionnary.
        """
        return await self._database.read_one(
            self.name,
            filter=filter,
            projection=projection,
            offset=offset,
            session=session,
            **kwargs,
        )

    async def read_one_by_id(
        self,
        id: str,
        *,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """Read one document from collection by ID.

        Arguments:
            id: The ID of the document to read.
            projection: Dictionary to filter documents fields to return.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A document as a dictionary. None if no document matched this _id.
        """
        return await self._database.read_one_by_id(
            self.name, id=id, projection=projection, session=session, **kwargs
        )

    async def create_one(
        self,
        document: Dict[str, Any],
        *,
        unique_key: Optional[str] = None,
        unique_filter: Optional[Dict[str, Any]] = None,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> InsertOneResult:
        """Create one document in collection.

        Arguments:
            document: The document's content as a dictionary.
            unique_key: Name of field in document that must be unique in collection.
            unique_filter: Dictionnary of string and values to consider document unique.
            session: The session to use when using transactions.
            kwargs: Additional arguments specified to backend.

        Returns:
            An insertion result.
        """
        return await self._database.create_one(
            self.name,
            document=document,
            unique_key=unique_key,
            unique_filter=unique_filter,
            session=session,
            **kwargs,
        )

    async def create_many(
        self,
        documents: List[Dict[str, Any]],
        *,
        unique_key: Optional[str] = None,
        unique_filter: Optional[Dict[str, Any]] = None,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> InsertManyResult:
        """Create many documents in collection.

        Arguments:
            documents: The list of document's content as dictionaries.
            session: The session to use when using transactions.
            unique_key: String denotating a field in the document that must be unique.
            unique_filter: Dictionnary of string and values to consider document unique.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An insertion result.
        """
        return await self._database.create_many(
            self.name,
            documents=documents,
            unique_key=unique_key,
            unique_filter=unique_filter,
            session=session,
            **kwargs,
        )

    async def delete_many(
        self,
        *,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> DeleteResult:
        """Delete many documents from collection.

        An empty filter means that all documents from collection should be removed.

        Arguments:
            filter: Dictionary to filter documents to delete.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A delete result.
        """
        return await self._database.delete_many(
            self.name, filter=filter, session=session, **kwargs
        )

    async def delete_one(
        self,
        *,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> DeleteResult:
        """Delete one document from collection.

        An empty filter means that the first document found in collection should be removed.

        Arguments:
            filter: Dictionary to filter documents to delete.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A delete result.
        """
        return await self._database.delete_one(
            self.name, filter=filter, session=session, **kwargs
        )

    async def delete_one_by_id(
        self,
        id: str,
        *,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> DeleteResult:
        """Delete one document from collection by ID.

        Arguments:
            id: The ID of the document to delete.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A delete result.
        """
        return await self._database.delete_one_by_id(
            self.name, id=id, session=session, **kwargs
        )

    async def delete_many_by_id(
        self,
        ids: List[str],
        *,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> DeleteResult:
        """Delete many documents from collection by IDs.

        Arguments:
            ids: The IDs of the documents to delete.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A deletion result.
        """
        return await self._database.delete_many_by_id(
            self.name, ids=ids, session=session, **kwargs
        )

    async def update_many(
        self,
        update_document: Dict[str, Any],
        *,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> UpdateResult:
        """Update many documents from collection by IDs.

        Arguments:
            ids: The IDs of the documents to update.
            update_document: The data to update in the documents as a dictionary.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An update result.
        """
        return await self._database.update_many(
            self.name,
            update_document=update_document,
            filter=filter,
            session=session,
            **kwargs,
        )

    async def update_one(
        self,
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
        return await self._database.update_one(
            self.name,
            update_document=update_document,
            filter=filter,
            session=session,
            **kwargs,
        )

    async def update_one_by_id(
        self,
        id: str,
        update_document: Dict[str, Any],
        *,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> UpdateResult:
        """Update one document from collection by ID.

        Arguments:
            id: The ID of the document to update.
            update_document: The data to update in the document as a dictionary.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An update result.
        """
        return await self._database.update_one_by_id(
            self.name,
            id=id,
            update_document=update_document,
            session=session,
            **kwargs,
        )

    async def update_many_by_id(
        self,
        ids: List[str],
        update_document: Dict[str, Any],
        *,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> UpdateResult:
        """Update many documents from collection by IDs.

        Arguments:
            collection: The collection to query.
            ids: The IDs of the documents to update.
            update_document: The data to update in the documents as a dictionary.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An update result.
        """
        return await self._database.update_many_by_id(
            self.name,
            ids=ids,
            update_document=update_document,
            session=session,
            **kwargs,
        )

    @property
    def start_transaction(self):  # type: ignore[no-untyped-def]
        """Initializes a transaction context by returning a session objet to use with
        collection operations.

        Expected behavior: If no error is raised within the context manager then
        the transaction is committed on its exit, otherwise the transaction
        (and thus the operations done within it) are aborted.
        """
        return self._database.start_transaction


__all__ = ["Collection"]
