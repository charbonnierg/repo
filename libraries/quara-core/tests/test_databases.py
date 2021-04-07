import pytest
from quara.api import Database
from quara.core.errors import DocumentNotUniqueError, PluginNotFoundError


@pytest.mark.asyncio
@pytest.mark.databases
async def test_bad_backend() -> None:
    with pytest.raises(PluginNotFoundError):
        Database("mongooose")


@pytest.mark.asyncio
@pytest.mark.databases
async def test_default_backend(database) -> None:
    # Database should be connected
    assert database._connected
    # Connect should not have any effet
    await database.connect()
    assert database._connected
    # Close the database
    await database.close()
    assert not database._connected
    # Close should not have any effet
    await database.close()
    assert not database._connected
    # Connect the database again
    await database.connect()
    # The database should be connected
    assert database._connected


@pytest.mark.asyncio
@pytest.mark.databases
async def test_count_all(database: Database) -> None:
    """Test counting documents in collection."""
    col = database["test_count_all"]
    # Delete all documents
    await col.delete_many()
    # Ensure there are no documents
    assert (await col.count()) == 0
    # Create a document
    await col.create_one({"key": True})
    # Ensure there is 1 document
    assert (await col.count()) == 1
    # Create an other document
    await col.create_one({"key": False})
    # Ensure there are 2 documents
    assert (await col.count()) == 2
    # Ensure there is 1 document matching filter
    assert (await col.count(filter={"key": True})) == 1
    # Delete collection
    await col.delete_many()
    # Ensure there are not documents left
    assert await col.count() == 0


@pytest.mark.asyncio
@pytest.mark.databases
async def test_offset_and_limit(database: Database):
    col = database["test_offset_and_limit"]
    await col.delete_many()
    await col.create_one({"first": True})
    await col.create_one({"first": False})
    docs = await col.read_many(offset=1, limit=1)
    assert not docs[0]["first"]


@pytest.mark.asyncio
@pytest.mark.databases
async def test_iterate_many(database) -> None:
    """Test iterating over many documents in database."""
    col = database["test_iterate_many"]
    # Delete all documents
    await col.delete_many()
    # Insert documents
    documents = [{"key": True}] * 2 + [{"key": False}] * 2
    await col.create_many(documents)
    # Iterator over documents
    _idx = 0
    # Apply a filter
    async for doc in col.iterate_many(filter={"key": True}):
        _idx += 1
        assert _idx <= 2
        assert doc["key"]
    # Apply a limit
    docs = [doc async for doc in col.iterate_many(filter={"key": False}, limit=1)]
    assert len(docs) == 1
    assert not docs[0]["key"]


@pytest.mark.asyncio
@pytest.mark.databases
async def test_iterate_many_projections(database) -> None:
    """Test iterating over many documents in database."""
    col = database["test_iterate_many"]
    # Delete all documents
    await col.delete_many()
    # Insert documents
    documents = [{"key": True, "a": 1, "b": 2}] * 2 + [
        {"key": False, "a": 1, "b": 2}
    ] * 2
    await col.create_many(documents)
    # Iterator over documents
    _idx = 0
    # Apply a filter
    async for doc in col.iterate_many(filter={"key": True}, projection={}):
        _idx += 1
        assert _idx <= 2
        assert "key" not in doc
        assert "a" not in doc
        assert "b" not in doc
        assert "id" in doc
    # Apply a limit
    docs = [
        doc
        async for doc in col.iterate_many(
            filter={"key": False}, limit=1, projection={"key": 1, "a": 1, "id": 0}
        )
    ]
    assert len(docs) == 1
    assert not docs[0]["key"]
    assert "a" in docs[0]
    assert "b" not in docs[0]
    assert "id" not in docs[0]


@pytest.mark.asyncio
@pytest.mark.databases
async def test_create_one(database) -> None:
    """Tests single document creation and retrieval."""
    # Use a specific collection
    col = database["test_create_one"]
    # Clean collection
    await col.delete_many()
    assert await col.read_one() is None
    # Define some document
    document = {"key1": "value1", "key2": 2}
    # Create it
    r = await col.create_one(document)
    # Check that we get an id back
    assert isinstance(r.inserted_id, str)
    # Check that we can read it back
    result = await col.read_one_by_id(r.inserted_id)
    assert result == await col.read_one()
    # Assert ID did not change
    assert result["id"] == r.inserted_id
    # Test if result is a superset of inserted dict (it has other attributes such as "id")
    assert document.items() <= result.items()


@pytest.mark.asyncio
@pytest.mark.databases
async def test_id_in_read_result(database) -> None:
    """Tests document retrieval 'id' key presence and '_id' key removal."""
    # Use a specific collection
    col = database["test_id_in_read_result"]
    # Create some dict
    doc = {"key1": "value1", "key2": 2}
    # Insert it
    r = await col.create_one(doc)
    # Read it back using insert result ID (we just want the id)
    result = await col.read_one_by_id(r.inserted_id, projection={"id": 1})
    # Assert that databases returning "id" as "_id" sanitize their output
    assert "_id" not in result
    assert "id" in result
    assert result["id"] == r.inserted_id


@pytest.mark.asyncio
@pytest.mark.databases
async def test_create_many(database) -> None:
    """Tests multiple documents creation and retrieval."""
    col = database["test_create_many"]
    # Clean collection
    await col.delete_many()
    # Create a bunch of documents
    docs = [{"foo": "bar"}] * 10
    # And a single document having a different field
    docs += [{"baz": "bar"}]
    # Insert the documents
    r = await col.create_many(docs)
    # Count documents
    _count = await col.count()
    # Test count
    assert _count == 11
    # Read the documents back
    # Note that mongo preserve orders. This might not be too for others database and thus this test might fail.
    assert (await col.read_many_by_id(r.inserted_ids, projection={"id": 0})) == docs
    # Check for inserted values using read_many_by_attr
    results = await col.read_many_by_attr(foo="bar")
    assert len(results) >= 10
    # Look for the other value
    results = await col.read_many_by_attr(baz="bar")
    assert len(results) >= 1
    # Look for non existing value
    results = await col.read_many_by_attr(baz="baaaaaar")
    assert len(results) == 0
    # Delete all documents
    await col.delete_many_by_id(ids=r.inserted_ids)
    # Ensure that collection is empty
    await col.count() == _count


@pytest.mark.asyncio
@pytest.mark.databases
async def test_various_iterate(database):
    col = database["test_create_one_unique_key"]
    await col.delete_many()
    doc = {"key": 1}
    res = await col.create_one(doc)
    all_docs = await col.read_all(projection={})
    assert len(all_docs) == 1
    assert [doc async for doc in col.iterate_all(projection={})] == all_docs
    assert [
        doc
        async for doc in col.iterate_many_by_id(ids=[res.inserted_id], projection={})
    ] == all_docs
    assert (
        len(
            [
                doc
                async for doc in col.iterate_many_by_attr(
                    key=0, ids=[res.inserted_id], projection={}
                )
            ]
        )
        == 0
    )
    assert [
        doc async for doc in col.iterate_many_by_attr(key=1, projection={})
    ] == all_docs


@pytest.mark.asyncio
@pytest.mark.databases
async def test_update_many(database: Database):
    col = database["test_update_many"]
    # Clean database
    await col.delete_many()
    # Insert some documents
    docs = [{"test": True}] * 2
    r = await col.create_many(docs)
    # Update documents
    await col.update_many({"test": False}, filter={"test": True})
    # Query documents
    assert len(await col.read_many(filter={"test": True})) == 0
    assert len(await col.read_many(filter={"test": False})) == 2
    # Update documents
    await col.update_many_by_id(r.inserted_ids[0], {"test": True})
    # Query documents
    assert len(await col.read_many(filter={"test": True})) == 1
    assert len(await col.read_many(filter={"test": False})) == 1


@pytest.mark.asyncio
@pytest.mark.databases
async def test_create_one_unique(database):
    col = database["test_create_one_unique_key"]
    await col.delete_many()
    doc = {"key": 1, "other": 1}
    await col.create_one(doc, unique_key="key")
    await col.create_one(doc, unique_key="key", unique_filter={"other": 2})
    await col.delete_many()
    await col.create_one(doc, unique_filter={"key": {"$eq": 1}})
    with pytest.raises(DocumentNotUniqueError):
        await col.create_one(doc, unique_key="key")
    with pytest.raises(DocumentNotUniqueError):
        await col.create_one(doc, unique_filter={"key": 1})
    with pytest.raises(DocumentNotUniqueError):
        await col.create_one(doc, unique_filter={"key": {"$eq": 1}})


@pytest.mark.asyncio
@pytest.mark.databases
async def test_create_many_unique(database):
    col = database["test_create_one_unique_key"]
    await col.delete_many()
    docs = [{"key": 1, "other": 1}]
    docs2 = [{"key": 1, "other": 2}]

    await col.create_many(docs, unique_key="key")
    await col.create_many(docs2, unique_key="key", unique_filter={"other": 2})
    await col.delete_many()
    await col.create_many(docs, unique_filter={"key": {"$eq": 1}})
    with pytest.raises(DocumentNotUniqueError):
        await col.create_many(docs, unique_key="key")
    with pytest.raises(DocumentNotUniqueError):
        await col.create_many(docs2, unique_filter={"key": 1})
    with pytest.raises(DocumentNotUniqueError):
        await col.create_many(docs2, unique_filter={"key": {"$eq": 1}})
