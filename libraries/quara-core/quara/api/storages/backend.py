from __future__ import annotations

from abc import abstractmethod
from typing import Any, List

from quara.core.plugins import Plugin

from .bucket import Bucket


class StorageBackend(Plugin):
    """Object storage resource, working with buckets and files.

    Exposes basic operations on buckets (create, get, delete, list, exists) and
    files contained in buckets (create, get, delete, list, exists).
    """

    @abstractmethod
    def __init__(self, **kwargs: Any) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def create_bucket(self, name: str, *, exist_ok: bool = False) -> Bucket:
        """Create a bucket. If exist_ok=True, raises an error if bucket already exists.

        Args:
            name: name of the bucket to create
            exist_ok: If the bucket already exists, does not raise an exception
                when exists_ok=True and simply return existing bucket. Defaults to False.

        Raises:
            S3ResourceError: Bucket already exists (if exists_ok=False), or global S3 error.

        Returns:
            Bucket: bucket object depicting online bucket
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def delete_bucket(self, name: str) -> None:
        """Delete a bucket

        Args:
            name: name of the bucket to fetch

        Raises:
            S3ResourceError: Specified bucket does not exists, or global S3 error.

        Returns:
            Bucket: bucket object depicting online bucket
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def list_buckets(self) -> List[str]:
        """List existing buckets

        Raises:
            S3ResourceError: Global S3 error.

        Returns:
            List[str]: list of existing bucket names
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def bucket_exists(self, name: str) -> bool:
        """Check if a bucket exists

        Args:
            name: name of the bucket to test

        Raises:
            S3ResourceError: Global S3 error.

        Returns:
            bool: True if bucket exists, false otherwise
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def get_object(self, bucket: str, name: str) -> bytes:
        """Get an object in a specified bucket

        Args:
            bucket: name of the bucket containing the object
            name: name of the object to fetch

        Raises:
            S3ResourceError: Bucket or object does not exist, or global S3 error.

        Returns:
            bytes: object's content
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def put_object(self, bucket: str, name: str, data: bytes) -> None:
        """Store an object in a specified bucket. If the object already exists, overwrite it.

        Args:
            bucket: name of the bucket containing the object
            name: name of the object to create
            data: object's content

        Raises:
            S3ResourceError: bucket does not exist or global S3 error.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def delete_object(self, bucket: str, name: str) -> None:
        """Delete the specified object in the specified bucket.

        Args:
            bucket: name of the bucket containing the object
            name: name of the object to delete

        Raises:
            S3ResourceError: Bucket or object does not exist, or global S3 error.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def list_objects(self, bucket: str) -> List[str]:
        """List objects in the specified bucket.

        Args:
            bucket: name of the bucket to consider

        Raises:
            S3ResourceError: Bucket does not exist or global S3 error.

        Returns:
            List[str]: list of object names
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def object_exists(self, bucket: str, name: str) -> bool:
        """Check if an object exists in the specified bucket.

        Args:
            bucket: bucket: name of the bucket containing the object
            name: name of the object to test

        Raises:
            S3ResourceError: Bucket does not exist or global S3 error.

        Returns:
            bool: True if object exists, false otherwise
        """
        raise NotImplementedError  # pragma: no cover


__all__ = ["StorageBackend"]
