from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from loguru import logger
from quara.api.databases.context import DatabaseContext
from quara.core.errors import ClientNotConnectedError, DocumentNotUniqueError
from quara.core.plugins import Pluggable

from .backend import DatabaseBackend
from .collection import Collection
from .defaults import (
    DEFAULT_FILTER,
    DEFAULT_LIMIT,
    DEFAULT_OFFSET,
    DEFAULT_PROJECTION,
    DEFAULT_SESSION,
)
from .results import DeleteResult, InsertManyResult, InsertOneResult, UpdateResult


class Database(Pluggable[DatabaseBackend]):
    """A base class for asynchronous client to operate CRUD operations on documents collection.

    ### Notes:

    * By default the "mongo" backend is used. It accepts the following arguments:
        - host: The listening host of mongodb server
        - port: The listening port of mongodb server
        - name: The mongodb database to use

    * Connection to database is performed only when calling the `Database.connect()` method.

    * You can use the context manager to automatically close database connections:

    ### Example usages:

    - Using a context manager:

    ```
    # Create database using context manager
    async with Database(name="quara") as db:
        # Do some work
        doc = await db.read_one()
    ```

    - Closing the connections manually:

    ```
    # Create database
    db = Database(name="quara")
    # Connect manually
    await db.connect()
    # Do some work
    doc = await db.read_one()
    # Close manually
    await db.close()
    ```


    ### References:

    * MongoDB query and projection operators: <https://docs.mongodb.com/manual/reference/operator/query/>
    * Query MongoDB Documents: <https://docs.mongodb.com/manual/tutorial/query-documents/>
    """

    __group__ = "quara.databases"
    __default_backend__: str = "mongo"

    def __init__(self, backend: Optional[str] = None, /, **kwargs: Any) -> None:
        """Create a new database client instance.

        Arguments:
            backend: The backend plugin to use.
            kwargs: Additional arguments specific to given backend.
        """
        # self._backend attribute is loaded using the __init__() method of parent class
        super().__init__(backend, **kwargs)
        # Do not connect on init
        self._connected = False

    @classmethod
    def from_context(
        cls, context: Union[DatabaseContext, Dict[str, Any], None] = None
    ) -> Database:
        """Create a new database from context."""
        if context:
            if isinstance(context, DatabaseContext):
                options = context.dict(exclude_unset=True)
            else:
                options = context
        else:
            options = {}
        options.pop("enabled", None)
        return cls(**options)

    async def connect(self, **kwargs: Any) -> None:
        """Connect to the database.

        Arguments:
            kwargs: Additional arguments specific to backend.
        """
        # Only attempt to connect when not connected yet
        if not self._connected:
            # Call connect method from backend
            await self._backend.connect(**kwargs)
            # Set "_connected" instance attribute to True
            self._connected = True

    async def close(self, **kwargs: Any) -> None:
        """Close connection the database.

        Arguments:
            kwargs: Additional arguments specified to backend.
        """
        # Only attempt to disconnnect when already connected
        if self._connected:
            # Call close method from backend
            await self._backend.close(**kwargs)
            # Set "_connected" instance attribute to False
            self._connected = False

    async def __aenter__(self) -> Database:
        """Asynchronous context manager enter method.

        ### References:

        * `__aenter__` documentation: <https://docs.python.org/3/reference/datamodel.html#object.__aenter__>
        """
        # Connect before yielding resource
        await self.connect()
        # Return instance
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        """Asynchronous context manager exit method.

        ### References:

        * `__aexit__` documentation: <https://docs.python.org/3/reference/datamodel.html#object.__aexit__>
        """
        # Always close connections before exiting
        await self.close()

    def __getitem__(self, name: str) -> Collection:
        """Get a collection by name.

        ### References:

        * `__getitem__` documentation: <https://docs.python.org/3/reference/datamodel.html#object.__getitem__>
        """
        # Return a new collection instance
        return Collection(self, name)

    def _check_connection(self) -> None:
        if not self._connected:
            raise ClientNotConnectedError("Database client is not connected yet")

    async def count(
        self,
        /,
        collection: str,
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
        self._check_connection()
        count: int = await self._backend.count(
            collection, filter=filter, session=session, **kwargs
        )
        return count

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

        ### References:

        * PEP 525 -- Asynchronous Generators: <https://www.python.org/dev/peps/pep-0525/>
        * `typing.AsyncGenerator` documentation: <https://docs.python.org/3/library/typing.html#typing.AsyncGenerator>
        """
        self._check_connection()
        async for document in self._backend.iterate_many(
            collection,
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
        collection: str,
        /,
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
            collection: The collection to query documents from.
            limit: The maximum documents of items to fetch.
            filter: The filter to apply as a dict.
            projection: Dictionary to filter documents fields to return.
            offset: The offset from which start fetching documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A list of documents as dictionaries.
        """
        cursor = self.iterate_many(
            collection,
            filter=filter,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        )
        return [document async for document in cursor]

    async def iterate_all(
        self,
        collection: str,
        /,
        *,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Return an iterator on all documents from collection.

        Arguments:
            collection: The collection to query documents from.
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to iterate on.
            offset: The offset from which start iterating on documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An asynchronous generator yielding documents as dictionaries.
        """
        async for document in self.iterate_many(
            collection,
            filter=None,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        ):
            yield document

    async def read_all(
        self,
        collection: str,
        /,
        *,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Read all documents from collection.

        Arguments:
            collection: The collection to query documents from.
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to fetch.
            offset: The offset from which start fetching documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A list of documents as dictionaries.
        """
        return await self.read_many(
            collection,
            projection=projection,
            filter=None,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        )

    async def iterate_many_by_id(
        self,
        collection: str,
        /,
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
            collection: The collection to query documents from.
            ids: The IDs of the documents to iterate on.
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to iterate on.
            offset: The offset from which start iterating on documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An asynchronous generator yielding documents as dictionaries.
        """
        async for document in self.iterate_many(
            collection,
            filter={"id": ids},
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        ):
            yield document

    async def iterate_many_by_attr(
        self,
        collection: str,
        /,
        *,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        limit: int = DEFAULT_LIMIT,
        offset: int = DEFAULT_OFFSET,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Return an iterator on documents from collection by their attributes.

        Arguments:
            collection: The collection to query documents from.
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to iterate on.
            offset: The offset from which start iterating on documents.
            session: The session to use when using transactions.
            **kwargs: Arguments containing attributes defining filter.

        Returns:
            An asynchronous generator yielding documents as dictionaries.
        """
        async for document in self.iterate_many(
            collection,
            filter=kwargs,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
        ):
            yield document

    async def read_many_by_id(
        self,
        collection: str,
        /,
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
            collection: The collection to query.
            ids: The IDs of the documents to read.
            projection: Dictionary to filter documents fields to return.
            limit: The maximum documents of items to fetch.
            offset: The offset from which start fetching documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A list of matching documents as dictionaries.
        """
        return await self.read_many(
            collection,
            filter={"id": ids},
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
            **kwargs,
        )

    async def read_many_by_attr(
        self,
        collection: str,
        /,
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
        return await self.read_many(
            collection,
            filter=kwargs,
            projection=projection,
            limit=limit,
            offset=offset,
            session=session,
        )

    async def read_one(
        self,
        collection: str,
        /,
        filter: Optional[Dict[str, Any]] = DEFAULT_FILTER,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        *,
        offset: int = 0,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """Find the first document matching filter or return None.

        Arguments:
            collection: The collection to query.
            filter: The filter to apply as a dict.
            projection: Dictionary to filter documents fields to return.
            offset: The offset from which start fetching documents.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            None or the document as dictionnary.
        """
        # Use read many method with limit=1
        docs = await self.read_many(
            collection,
            filter=filter,
            projection=projection,
            limit=1,
            offset=offset,
            session=session,
            **kwargs,
        )
        # docs is a list, if it's empty it evaluates to False
        if docs:
            # Not empty, return first element
            return docs[0]
        else:
            # Empty, return None
            return None

    async def read_one_by_id(
        self,
        collection: str,
        /,
        id: str,
        *,
        projection: Optional[Dict[str, Any]] = DEFAULT_PROJECTION,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """Read one document from collection by ID.

        Arguments:
            collection: The collection to query.
            id: The ID of the document to read.
            projection: Dictionary to filter documents fields to return.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A document as a dictionary. None if no document matched this _id.
        """
        return await self.read_one(
            collection,
            filter={"id": id},
            projection=projection,
            session=session,
            **kwargs,
        )

    async def create_one(
        self,
        collection: str,
        /,
        document: Dict[str, Any],
        *,
        unique_key: Optional[str] = None,
        unique_filter: Optional[Dict[str, Any]] = None,
        session: Optional[Any] = DEFAULT_SESSION,
        **kwargs: Any,
    ) -> InsertOneResult:
        """Create one document in collection.

        Arguments:
            collection: The collection to query documents from.
            document: The document's content as a dictionary.
            unique_key: Name of field in document that must be unique in collection.
            unique_filter: Dictionnary of string and values to consider document unique.
            session: The session to use when using transactions.
            kwargs: Additional arguments specified to backend.

        Returns:
            An insertion result.
        """
        self._check_connection()
        # Result will be of int type
        result: InsertOneResult
        # Check if unique_filter was provided
        if unique_filter:
            # If unique_key was also provided
            if unique_key:
                # Log a warning
                logger.warning(
                    "unique_key argument is ignored because unique_filter is also provided."
                )
                # Set unique_key to None
                unique_key = None
        # Check if unique_key was provided
        elif unique_key:
            # And construct unique_filter from unique_key and document
            unique_filter = {unique_key: document[unique_key]}
        # No need to check for uniqueness
        else:
            result = await self._backend.create_one(
                collection, document=document, session=session, **kwargs
            )
            return result
        # If we're here, we need to check for uniqueness
        # Count documents from collection
        _count = await self.count(
            collection,
            # Where the field unique_key is equal to document[unique_key]
            filter=unique_filter,
            session=session,
        )
        if _count:
            # There is already a document with this key/value
            raise DocumentNotUniqueError(
                f"Document is not unique. Filters with duplicates: {unique_filter}"
            )
        # Create the document using create_one from backend
        result = await self._backend.create_one(
            collection, document=document, session=session, **kwargs
        )
        return result

    async def create_many(
        self,
        collection: str,
        /,
        documents: List[Dict[str, Any]],
        *,
        unique_key: Optional[str] = None,
        unique_filter: Optional[Dict[str, Any]] = None,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> InsertManyResult:
        """Create many documents in collection.

        Arguments:
            collection: The collection to query.
            documents: The list of document's content as dictionaries.
            session: The session to use when using transactions.
            unique_key: String denotating a field in the document that must be unique.
            unique_filter: Dictionnary of string and values to consider document unique.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An insertion result.
        """
        self._check_connection()
        result: InsertManyResult
        # Check if unique_filter was provided
        if unique_filter:
            # If unique_key was also provided
            if unique_key:
                # Log a warning
                logger.warning(
                    "unique_key argument is ignored because unique_filter is also provided."
                )
                # Set unique_key to None
                unique_key = None
        # Check if unique_key was provided
        elif unique_key:
            # And construct unique_filter from unique_key and document
            unique_filter = {
                unique_key: {"$in": [doc[unique_key] for doc in documents]}
            }
        # No need to check for uniqueness
        else:
            # Use create_many method from backend
            result = await self._backend.create_many(
                collection, documents=documents, session=session, **kwargs
            )
            return result
        # If we're here, we need to check for uniqueness
        # Count documents from collection
        if await self.count(
            collection,
            filter=unique_filter,
            session=session,
        ):
            # There is already a document with this key/value
            raise DocumentNotUniqueError(
                "Non unique documents present in insert. No document was inserted."
            )
        # Create the documents
        result = await self._backend.create_many(
            collection, documents=documents, session=session, **kwargs
        )
        return result

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
        self._check_connection()
        result: DeleteResult = await self._backend.delete_many(
            collection, filter=filter, session=session, **kwargs
        )
        return result

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
        self._check_connection()
        result: DeleteResult = await self._backend.delete_one(
            collection, filter=filter, session=session, **kwargs
        )
        return result

    async def delete_one_by_id(
        self,
        collection: str,
        /,
        id: str,
        *,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> DeleteResult:
        """Delete one document from collection by ID.

        Arguments:
            collection: The collection to query.
            id: The ID of the document to delete.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A delete result.
        """
        result: DeleteResult = await self._backend.delete_many(
            collection, filter={"id": id}, session=session, **kwargs
        )
        return result

    async def delete_many_by_id(
        self,
        collection: str,
        /,
        ids: List[str],
        *,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> DeleteResult:
        """Delete many documents from collection by IDs.

        Arguments:
            collection: The collection to query.
            ids: The IDs of the documents to delete.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            A deletion result.
        """
        result: DeleteResult = await self._backend.delete_many(
            collection, filter={"id": ids}, session=session, **kwargs
        )
        return result

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
        self._check_connection()
        result: UpdateResult = await self._backend.update_many(
            collection,
            update_document=update_document,
            filter=filter,
            session=session,
            **kwargs,
        )
        return result

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
        self._check_connection()
        result: UpdateResult = await self._backend.update_one(
            collection,
            update_document=update_document,
            filter=filter,
            session=session,
            **kwargs,
        )
        return result

    async def update_one_by_id(
        self,
        collection: str,
        /,
        id: str,
        update_document: Dict[str, Any],
        *,
        session: Optional[Any] = None,
        **kwargs: Any,
    ) -> UpdateResult:
        """Update one document from collection by ID.

        Arguments:
            collection: The collection to query.
            id: The ID of the document to update.
            update_document: The data to update in the document as a dictionary.
            session: The session to use when using transactions.
            kwargs: Additional keyword arguments propagated to the backend client.

        Returns:
            An update result.
        """
        return await self.update_one(
            collection,
            update_document=update_document,
            filter={"id": id},
            session=session,
            **kwargs,
        )

    async def update_many_by_id(
        self,
        collection: str,
        /,
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
        result: UpdateResult = await self._backend.update_many(
            collection,
            filter={"id": ids},
            update_document=update_document,
            session=session,
            **kwargs,
        )
        return result

    @property
    def start_transaction(self):  # type: ignore[no-untyped-def]
        """Initializes a transaction context by returning a session objet to use with
        collection operations.

        Expected behavior: If no error is raised within the context manager then
        the transaction is committed on its exit, otherwise the transaction
        (and thus the operations done within it) are aborted.
        """
        # I'm not sure of the consequences of checking connection at this level...
        # self._check_connection()
        return self._backend.start_transaction

    async def destroy(self) -> None:
        """Destroy the whole database."""
        self._check_connection()
        await self._backend.destroy()


__all__ = ["Database"]
