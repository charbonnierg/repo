# import pytest
# from quara.api import Storage
# from quara.api.storages import Bucket
# from quara.core.errors import (
#     BucketAlreadyExists,
#     NoSuchBucket,
#     NoSuchKey,
#     S3ResourceError,
# )


# @pytest.fixture
# async def bucket(storage: Storage) -> Bucket:
#     """Returns a bucket created (and eventually deleted on test exit if it still
#     exists) with the default object storage resource.
#     """
#     test_bucket = "temporary-test-bucket"
#     # Get the bucket
#     bucket: Bucket = storage[test_bucket]
#     # Create it
#     await bucket.create(True)
#     with pytest.raises(BucketAlreadyExists):
#         await bucket.create(False)
#     # Yield bucket to test case
#     yield bucket
#     # Clean object storage if bucket still present
#     if await storage.bucket_exists(bucket.name):
#         # First delete potential files still in the bucket
#         for object_name in await bucket.list_objects():
#             await bucket.delete_object(object_name)
#         # Delete bucket not used anymore
#         await bucket.delete()


# @pytest.mark.asyncio
# @pytest.mark.storages
# @pytest.mark.azure
# async def test_storage_s3(storage: Storage) -> None:
#     """Basic tests on object storage resource, file and bucket creation/retrieval."""
#     # Take a bucket
#     bucket = storage["test-azure-storage-basic"]
#     # Ensure it's deleted
#     try:
#         await bucket.delete()
#     except NoSuchBucket:
#         pass
#     # Create it again
#     await bucket.create()
#     # Create some test data
#     test_data = b"{'test': True}"
#     test_filename = "test_data.json"

#     assert bucket.name == "test-azure-storage-basic"
#     # Put and retrieve object and compare content
#     await bucket.put_object(test_filename, test_data)
#     assert await bucket.object_exists(test_filename)
#     assert await bucket.get_object(test_filename) == test_data

#     # Clean object storage
#     await bucket.delete_object(test_filename)
#     await bucket.delete()


# @pytest.mark.asyncio
# @pytest.mark.storages
# @pytest.mark.azure
# async def test_storage_s3_from_bucket_scope(bucket: Bucket) -> None:
#     """Tests using the Bucket structure to perform operations through, such as file uploads."""
#     test_data = b"{'test': True}"
#     test_filename = "test_data.json"

#     # Put and retrieve object and compare content
#     await bucket.put_object(test_filename, test_data)
#     assert await bucket.get_object(test_filename) == test_data

#     # Verify list output
#     objects = await bucket.list_objects()
#     assert len(objects) == 1
#     assert objects[0] == test_filename


# @pytest.mark.asyncio
# @pytest.mark.storages
# @pytest.mark.azure
# async def test_storage_s3_list_bucket(bucket: Bucket) -> None:
#     """Tests bucket listing methods."""
#     storage = bucket.client
#     buckets = await storage.list_buckets()
#     buckets_count = len(buckets)
#     # Verify list output. Don't check for equality, it makes the tests flaky.
#     assert buckets_count >= 1
#     # Check that the bucket exist.
#     # Note: iterator will break on first match
#     assert any(bucket.name == name for name in buckets)
#     # Delete bucket and check again
#     await storage.delete_bucket(bucket.name)
#     buckets = await storage.list_buckets()
#     # Verify list output
#     assert len(buckets) == buckets_count - 1


# @pytest.mark.asyncio
# @pytest.mark.storages
# @pytest.mark.azure
# async def test_get_not_exist(storage: Storage) -> None:
#     bucket_name = "test-get-not-exist"
#     try:
#         await storage.delete_bucket(bucket_name)
#     except NoSuchBucket:
#         pass
#     b = await storage.get_bucket(bucket_name)
#     assert b is None
#     bucket = await storage.create_bucket(bucket_name)
#     with pytest.raises(NoSuchKey):
#         await bucket.get_object("does-not-exist")


# @pytest.mark.asyncio
# @pytest.mark.storages
# @pytest.mark.azure
# async def test_delete_not_exist(storage: Storage) -> None:
#     try:
#         await storage.delete_bucket("test-not-exist")
#     except NoSuchBucket:
#         pass
#     res = await storage.get_bucket("test-not-exist")
#     assert res is None
#     with pytest.raises(NoSuchBucket):
#         await storage.delete_object("test-not-exist", "key")
#     await storage.create_bucket("test-not-exist")
#     # Deleting an object that does not exist does not raise an error.
#     await storage.delete_object("test-not-exist", "key")
#     await storage.delete_object("test-not-exist", "key")


# @pytest.mark.asyncio
# @pytest.mark.storages
# @pytest.mark.azure
# async def test_storage_s3_recreate_bucket(bucket: Bucket) -> None:
#     """Tests error raising macanisms for already existing bucket on creation."""
#     storage = bucket.client

#     # Test if it is OK it already exists
#     same_bucket = await storage.create_bucket(bucket.name, exist_ok=True)
#     assert bucket.name == same_bucket.name

#     # Test if not OK it already exists
#     with pytest.raises(S3ResourceError):
#         same_bucket = await storage.create_bucket(
#             bucket.name
#         )  # exists_ok=False by default


# @pytest.mark.asyncio
# @pytest.mark.storages
# @pytest.mark.azure
# async def test_storage_s3_raise_exception(storage: Storage) -> None:
#     """Tests diverse exception raising on object operations."""
#     test_bucket = "test-bucket-not-exists"
#     try:
#         await storage.delete_bucket(test_bucket)
#     except NoSuchBucket:
#         pass
#     test_filename = "test_data.json"
#     test_data = b"{'test': True}"

#     # Getting an object from a bucket that does not exist raise a NoSuchBucket error
#     with pytest.raises(NoSuchBucket):
#         await storage.get_object(test_bucket, test_filename)

#     # Checking if an object exist does not raise an error
#     await storage.object_exists(test_bucket, test_filename)

#     # Putting an object into a bucket that does not exist raises an error
#     with pytest.raises(NoSuchBucket):
#         await storage.put_object(test_bucket, test_filename, test_data)

#     # Deleting an object from a bucket that does not exist raises an error
#     with pytest.raises(NoSuchBucket):
#         await storage.delete_object(test_bucket, test_filename)

#     # Listing objects from a bucket that does not exist raises an error
#     with pytest.raises(NoSuchBucket):
#         await storage.list_objects(test_bucket)
