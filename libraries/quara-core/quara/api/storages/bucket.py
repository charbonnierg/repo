from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:  # pragma: no cover
    from .client import Storage


class Bucket:
    """Representation of an object storage bucket."""

    def __init__(self, client: Storage, name: str) -> None:
        self.name = name
        self.client = client

    async def get_object(self, name: str) -> bytes:
        """Get an object from the bucket."""
        return await self.client.get_object(self.name, name)

    async def put_object(self, name: str, data: bytes) -> None:
        """Put object into the bucket.

        Warning: this methold only accepts bytes, make sure to serialize
        your data properly.
        """
        return await self.client.put_object(self.name, name, data)

    async def delete_object(self, name: str) -> None:
        """Delete object from the bucket."""
        return await self.client.delete_object(self.name, name)

    async def list_objects(self) -> List[str]:
        """List all objects in the bucket."""
        return await self.client.list_objects(self.name)

    async def object_exists(self, name: str) -> bool:
        """Check if object exists in the bucket."""
        return await self.client.object_exists(self.name, name)

    def __repr__(self) -> str:
        return f"Bucket(client={self.client}, name={self.name})"

    async def create(self, exist_ok: bool = False) -> None:
        """Create the bucket in object storage."""
        await self.client.create_bucket(self.name, exist_ok=exist_ok)

    async def delete(self) -> None:
        """Delete the bucket from object storage."""
        await self.client.delete_bucket(self.name)


__all__ = ["Bucket"]
