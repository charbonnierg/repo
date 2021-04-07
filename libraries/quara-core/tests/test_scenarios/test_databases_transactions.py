import pytest
from quara.api import Database
from quara.api.databases.results import InsertOneResult


class ErrorOccuredInOperation(Exception):
    pass


@pytest.mark.asyncio
@pytest.mark.databases
async def test_database_commit_transaction(
    database: Database,
) -> None:
    """Tests single document creation and retrieval."""
    col = database["test_transaction"]
    await col.delete_many()
    document = {"key1": "value1", "key2": 2}
    async with col.start_transaction() as transaction:
        insert_result = await col.create_one(document, session=transaction)
        # Test result within transaction
        assert isinstance(insert_result.inserted_id, str)
        result = await col.read_one_by_id(
            insert_result.inserted_id, session=transaction
        )
        assert result["id"] == insert_result.inserted_id
        # Test if result is a superset of inserted dict (it has other attributes such as "id")
        assert document.items() <= result.items()
    # Assert transaction is commited and saved
    result = await col.read_one_by_id(insert_result.inserted_id)
    assert result["id"] == insert_result.inserted_id
    # Test if result is a superset of inserted dict (it has other attributes such as "id")
    assert document.items() <= result.items()


@pytest.mark.asyncio
@pytest.mark.databases
async def test_database_abort_transaction(
    database: Database,
) -> None:
    """Tests single document aborted creation and retrieval."""
    document = {"key1": "value1", "key2": 2}
    col = database["test_abort_transaction"]
    await col.delete_many()
    insert_result = None
    try:
        async with database.start_transaction() as transaction:
            insert_result = await col.create_one(document, session=transaction)
            # Test result within transaction
            assert isinstance(insert_result.inserted_id, str)
            result = await col.read_one_by_id(
                insert_result.inserted_id, session=transaction
            )
            assert result["id"] == insert_result.inserted_id
            # Test if result is a superset of inserted dict (it has other attributes such as "id")
            assert document.items() <= result.items()
            # Simulate an error with a required linked operation, such as a resource usage that not went well
            raise ErrorOccuredInOperation
    except ErrorOccuredInOperation:
        _insert_result: InsertOneResult = insert_result
        # Assert transaction was aborted and nothing was actually inserted
        result = await col.read_one_by_id(_insert_result.inserted_id)
        assert result is None


@pytest.mark.asyncio
@pytest.mark.databases
async def test_collection_client_abort_multiple_transactions(
    database: Database,
) -> None:
    """Tests single document aborted creation and retrieval."""
    col = database["test_abort_multiple_transactions"]
    await col.delete_many()
    document = {"key1": "value1", "key2": 2}
    insert_result = await col.create_one(document)
    assert isinstance(insert_result.inserted_id, str)
    document_id = insert_result.inserted_id
    result = await col.read_one_by_id(insert_result.inserted_id)
    assert result["id"] == document_id
    # Test if result is a superset of inserted dict (it has other attributes such as "id")
    assert document.items() <= result.items()

    update = {"key2": "UPDATED", "key3": "UPDATED_TOO"}
    try:
        async with col.start_transaction() as transaction:
            # Update document
            result = await col.update_one_by_id(
                document_id, update, session=transaction
            )
            # Test result within transaction
            assert result.modified_count == 1
            result = await col.read_one_by_id(document_id, session=transaction)
            assert result["key1"] == document["key1"]
            for updated_value in update.items():
                assert result[updated_value[0]] == updated_value[1]
            # Delete document
            delete_result = await col.delete_one_by_id(document_id, session=transaction)
            assert delete_result.deleted_count == 1
            deleted_document = await col.read_one_by_id(
                document_id, session=transaction
            )
            assert deleted_document is None
            # Simulate an error with a required linked operation, such as a resource usage that not went well
            raise ErrorOccuredInOperation
    except ErrorOccuredInOperation:
        # Assert transaction was aborted and document was not deleted nor updated
        result = await col.read_one_by_id(document_id)
        assert result is not None
        assert result["id"] == document_id
        assert document.items() <= result.items()
