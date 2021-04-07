import json
import subprocess
from typing import Any, Dict, List, Optional

from azure.core.exceptions import AzureError, ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient
from quara.api import AsyncExecutor
from quara.api.storages import Bucket, StorageBackend
from quara.core.errors import (
    BucketAlreadyExistsError,
    NoSuchBucketError,
    NoSuchKeyError,
    ResourceUnavailableError,
    S3Error,
)


class AzureStorageError(S3Error):
    def __init__(self, msg: str, err: Exception):
        self.msg = msg
        self.err = err


class AzureStorageClient(StorageBackend):
    def __init__(
        self,
        connection_string: Optional[str] = None,
        *,
        container: str = "test-container",
        resource_group: str = "quara-ci",
        storage_account: str = "quaracistorage",
        max_workers: int = 4,
        worker_kwargs: Dict[str, Any] = {},
        **kwargs: Any,
    ):
        if not connection_string:
            _cmd = f"az storage account show-connection-string --resource-group {resource_group} --name {storage_account}"
            data = json.loads(subprocess.check_output(_cmd, shell=True).decode())
            connection_string = data["connectionString"]
        self._container = container
        self._client = BlobServiceClient.from_connection_string(
            conn_str=connection_string
        )
        self.executor = AsyncExecutor(max_workers=max_workers, **worker_kwargs)

    async def create_bucket(
        self, name: str, exist_ok: bool = False, **kwargs: Any
    ) -> Bucket:
        """Create a bucket in Azure Blob Storage."""
        try:
            await self.executor.run(self._client.create_container, name, **kwargs)
        except ResourceExistsError as err:
            if not exist_ok:
                raise BucketAlreadyExistsError(err)
        return Bucket(self, name)

    async def delete_bucket(self, name: str, **kwargs: Any) -> None:
        try:
            await self.executor.run(self._client.delete_container, name, **kwargs)
        except ResourceNotFoundError as err:
            raise NoSuchBucketError(err)
        except AzureError as err:
            raise AzureStorageError("Delete operation failed", err)

    async def list_buckets(self, **kwargs: Any) -> List[str]:
        try:
            return [
                bucket.name
                for bucket in await self.executor.run(
                    self._client.list_containers, **kwargs
                )
            ]
        except AzureError as error:
            raise AzureStorageError("List operation failed", error)

    async def bucket_exists(self, name: str, **kwargs: Any) -> bool:
        """Return True if a bucket exist, else return False."""
        try:
            container_client = self._client.get_container_client(name)
            await self.executor.run(container_client.get_container_access_policy)
        # If a ResourceNotFoundError is raised, container does not exist
        except ResourceNotFoundError:
            return False
        # If it's another error, we wan't handle it
        except AzureError as err:
            raise AzureStorageError("Exists operation failed", err)
        # Else the container does exist
        return True

    async def get_object(self, bucket: str, name: str, **kwargs: Any) -> bytes:
        """Get a single object from bucket by name."""
        # First get blob client
        blob_client = self._client.get_blob_client(bucket, name)
        try:
            # Try to download blob
            r = await self.executor.run(blob_client.download_blob)
        # Catch specific error
        except ResourceNotFoundError as err:
            # Raise correct error based on error code
            if err.error_code == "ContainerNotFound":  # type: ignore
                raise NoSuchBucketError(err)
            if err.error_code == "BlobNotFound":  # type: ignore
                raise NoSuchKeyError(err)
        # Catch generic azure error
        except AzureError as err:
            raise ResourceUnavailableError(err)
        # Return blob content as bytes
        content: bytes = await self.executor.run(r.readall)
        return content

    async def put_object(
        self, bucket: str, name: str, data: bytes, **kwargs: Any
    ) -> None:
        # First get blob client
        blob_client = self._client.get_blob_client(bucket, name)
        try:
            # Try to upload blob
            await self.executor.run(blob_client.upload_blob, data, **kwargs)
        # Catch specific error
        except ResourceNotFoundError as err:
            # Raise correct error based on error code
            if err.error_code == "ContainerNotFound":  # type: ignore
                raise NoSuchBucketError(err)
            if err.error_code == "BlobNotFound":  # type: ignore
                raise NoSuchKeyError(err)
        # Catch generic azrure error
        except AzureError as err:
            raise AzureStorageError("Put operation failed", err)

    async def delete_object(self, bucket: str, name: str, **kwargs: Any) -> None:
        # First get blob client
        blob_client = self._client.get_blob_client(bucket, name)
        try:
            # Try to download blob
            await self.executor.run(blob_client.delete_blob, **kwargs)
        # Catch specific error
        except ResourceNotFoundError as err:
            # Raise correct error based on error code
            if err.error_code == "ContainerNotFound":  # type: ignore
                raise NoSuchBucketError(err)
            if err.error_code == "BlobNotFound":  # type: ignore
                raise NoSuchKeyError(err)
        # Catch generic azrure error
        except AzureError as err:
            raise AzureStorageError("Delete operation failed", err)

    async def list_objects(self, bucket: str, **kwargs: Any) -> List[str]:
        try:
            container_client = self._client.get_container_client(bucket)

            # This should not be an inline function
            def _list() -> List[str]:
                return [blob.name for blob in container_client.list_blobs(**kwargs)]

            result: List[str] = await self.executor.run(_list)
            return result
        # If a ResourceNotFoundError is raised, container does not exist
        except ResourceNotFoundError:
            raise NoSuchBucketError(bucket)
        # If it's another error, we don't handle it
        except AzureError as err:
            raise AzureStorageError("List operation failed", err)

    async def object_exists(self, bucket: str, name: str, **kwargs: Any) -> bool:
        # First get blob client
        blob_client = self._client.get_blob_client(bucket, name)
        try:
            exists = await self.executor.run(blob_client.exists, **kwargs)
        except AzureError as error:
            raise AzureStorageError("Operation failed", error)
        # Exists might be none according to mypy so we check if it evaluates to True
        # instead of returning it directly
        if exists:
            return True
        return False
