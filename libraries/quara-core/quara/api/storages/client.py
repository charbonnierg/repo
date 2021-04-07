from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from quara.core.plugins import Pluggable

from .backend import StorageBackend
from .bucket import Bucket
from .context import StorageContext


class Storage(Pluggable[StorageBackend]):
    """Object storage resource, working with buckets and files.

    Exposes basic operations on buckets (create, get, delete, list, exists) and
    files contained in buckets (create, get, delete, list, exists).
    """

    __group__ = "quara.storages"
    __default_backend__: str = "minio"

    async def __aenter__(self) -> Storage:
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def create_bucket(
        self, name: str, *, exist_ok: bool = False, **kwargs: Any
    ) -> Bucket:
        """Create a bucket. If exist_ok=True, raises an error if bucket already exists.

        Args:
            name: name of the bucket to create
            exist_ok: If the bucket already exists, does not raise an exception
                when exists_ok=True and simply return existing bucket. Defaults to False.
            kwargs: Additional kwargs forwarded to backend client.

        Raises:
            S3ResourceError: Bucket already exists (if exists_ok=False), or global S3 error.

        Returns:
            Bucket: bucket object depicting online bucket
        """
        return await self._backend.create_bucket(name, exist_ok=exist_ok, **kwargs)  # type: ignore[no-any-return]

    @classmethod
    def from_context(
        cls, context: Union[StorageContext, Dict[str, Any], None] = None
    ) -> Storage:
        """Create a new database from context."""
        if context:
            if isinstance(context, StorageContext):
                options = context.dict(exclude_unset=True)
            else:
                options = context
        else:
            options = {}
        options.pop("enabled", None)
        return cls(**options)

    async def get_bucket(self, name: str, **kwargs: Any) -> Optional[Bucket]:
        """Fetch a bucket

        Args:
            name: name of the bucket to fetch
            kwargs: Additional kwargs forwarded to backend client.

        Raises:
            S3ResourceError: Specified bucket does not exists, or global S3 error.

        Returns:
            Bucket or None: bucket object depicting online bucket
        """
        if await self.bucket_exists(name, **kwargs):
            return Bucket(self, name)
        return None

    async def delete_bucket(self, name: str, **kwargs: Any) -> None:
        """Delete a bucket

        Args:
            name: name of the bucket to fetch
            kwargs: Additional kwargs forwarded to backend client.

        Raises:
            S3ResourceError: Specified bucket does not exists, or global S3 error.

        Returns:
            Bucket: bucket object depicting online bucket
        """
        await self._backend.delete_bucket(name, **kwargs)

    async def list_buckets(self, **kwargs: Any) -> List[str]:
        """List existing buckets

        Args:
            kwargs: Additional kwargs forwarded to backend client.

        Raises:
            S3ResourceError: Global S3 error.

        Returns:
            List[str]: list of existing bucket names
        """
        return await self._backend.list_buckets(**kwargs)  # type: ignore[no-any-return]

    async def bucket_exists(self, name: str, **kwargs: Any) -> bool:
        """Check if a bucket exists

        Args:
            name: name of the bucket to test
            kwargs: Additional kwargs forwarded to backend client.

        Raises:
            S3ResourceError: Global S3 error.

        Returns:
            bool: True if bucket exists, false otherwise
        """
        return await self._backend.bucket_exists(name, **kwargs)  # type: ignore[no-any-return]

    async def get_object(self, bucket: str, name: str, **kwargs: Any) -> bytes:
        """Get an object in a specified bucket

        Args:
            bucket: name of the bucket containing the object
            name: name of the object to fetch
            kwargs: Additional kwargs forwarded to backend client.

        Raises:
            S3ResourceError: Bucket or object does not exist, or global S3 error.

        Returns:
            bytes: object's content
        """
        return await self._backend.get_object(bucket, name, **kwargs)  # type: ignore[no-any-return]

    async def put_object(
        self, bucket: str, name: str, data: bytes, **kwargs: Any
    ) -> None:
        """Store an object in a specified bucket. If the object already exists, overwrite it.

        Args:
            bucket: name of the bucket containing the object
            name: name of the object to create
            data: object's content
            kwargs: Additional kwargs forwarded to backend client.

        Raises:
            S3ResourceError: bucket does not exist or global S3 error.
        """
        return await self._backend.put_object(bucket, name, data=data, **kwargs)  # type: ignore[no-any-return]

    async def delete_object(self, bucket: str, name: str, **kwargs: Any) -> None:
        """Delete the specified object in the specified bucket.

        Args:
            bucket: name of the bucket containing the object
            name: name of the object to delete
            kwargs: Additional kwargs forwarded to backend client.

        Raises:
            S3ResourceError: Bucket or object does not exist, or global S3 error.
        """
        await self._backend.delete_object(bucket, name, **kwargs)

    async def list_objects(self, bucket: str, **kwargs: Any) -> List[str]:
        """List objects in the specified bucket.

        Args:
            bucket: name of the bucket to consider
            kwargs: Additional kwargs forwarded to backend client.

        Raises:
            S3ResourceError: Bucket does not exist or global S3 error.

        Returns:
            List[str]: list of object names
        """
        return await self._backend.list_objects(bucket, **kwargs)  # type: ignore[no-any-return]

    async def object_exists(self, bucket: str, name: str, **kwargs: Any) -> bool:
        """Check if an object exists in the specified bucket.

        Args:
            bucket: bucket: name of the bucket containing the object
            name: name of the object to test

        Raises:
            S3ResourceError: Bucket does not exist or global S3 error.

        Returns:
            bool: True if object exists, false otherwise
        """
        return await self._backend.object_exists(bucket, name, **kwargs)  # type: ignore[no-any-return]

    def __getitem__(self, name: str) -> Bucket:
        return Bucket(self, name)


__all__ = ["Storage"]
