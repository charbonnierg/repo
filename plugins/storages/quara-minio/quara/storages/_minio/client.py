from io import BytesIO
from typing import Any, Dict, List

from minio import Minio
from minio.error import S3Error
from quara.api import AsyncExecutor
from quara.api.storages import Bucket
from quara.core.errors import (
    BucketAlreadyExistsError,
    BucketNotEmptyError,
    NoSuchBucketError,
    NoSuchKeyError,
)
from quara.core.errors import S3Error as _S3Error


class MinioError(_S3Error):
    def __init__(self, msg: str, err: Exception):
        self.msg = msg
        self.err = err


class AsyncioMinioClient:
    """An asynchronous implementation of Minio object storage client."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9000,
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        secure: bool = False,
        max_workers: int = 4,
        worker_kwargs: Dict[str, Any] = {},
        **kwargs: Any,
    ):
        self.host = host
        self.port = port
        self.endpoint = f"{host}:{port}"
        self.secure = secure
        self.access_key = access_key
        self.s3 = Minio(
            self.endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            **kwargs,
        )
        self.executor = AsyncExecutor(max_workers=max_workers, **worker_kwargs)

    async def create_bucket(
        self, name: str, exist_ok: bool = False, **kwargs: Any
    ) -> Bucket:
        try:
            await self.executor.run(self.s3.make_bucket, name, **kwargs)
        except S3Error as err:
            if err.code not in ("BucketAlreadyExists", "BucketAlreadyOwnedByYou"):
                raise MinioError("Ooops", err)
            if not exist_ok:
                raise BucketAlreadyExistsError(err)
        return Bucket(self, name)

    async def delete_bucket(self, name: str, **kwargs: Any) -> None:
        try:
            await self.executor.run(self.s3.remove_bucket, name, **kwargs)
        except S3Error as error:
            if error.code == "NoSuchBucket":
                raise NoSuchBucketError(error)
            if error.code == "BucketNotEmpty":
                raise BucketNotEmptyError(error)
            raise MinioError("Ooops", error)

    async def list_buckets(self) -> List[str]:
        try:
            return [
                bucket.name for bucket in await self.executor.run(self.s3.list_buckets)
            ]
        except S3Error as error:
            raise MinioError("Ooops", error)

    async def bucket_exists(self, name: str, **kwargs: Any) -> bool:
        try:
            if await self.executor.run(self.s3.bucket_exists, name, **kwargs):
                return True
            else:
                return False
        except S3Error as error:
            raise MinioError("Ooops", error)

    async def get_object(self, bucket: str, name: str, **kwargs: Any) -> bytes:
        try:
            response = await self.executor.run(
                self.s3.get_object, bucket, name, **kwargs
            )
            content: bytes = response.data
        except S3Error as error:
            if error.code == "NoSuchBucket":
                raise NoSuchBucketError(error)
            if error.code == "NoSuchKey":
                raise NoSuchKeyError(error)
            raise MinioError("Ooops", error)
        return content

    async def put_object(
        self, bucket: str, name: str, data: bytes, **kwargs: Any
    ) -> None:
        try:
            await self.executor.run(
                self.s3.put_object, bucket, name, BytesIO(data), len(data), **kwargs
            )
        except S3Error as error:
            if error.code == "NoSuchBucket":
                raise NoSuchBucketError(error)
            raise MinioError("Ooops", error)

    async def delete_object(self, bucket: str, name: str, **kwargs: Any) -> None:
        """Apparently minio does not raise an error when key does not exist."""
        try:
            await self.executor.run(self.s3.remove_object, bucket, name, **kwargs)
        except S3Error as error:
            if error.code == "NoSuchBucket":
                raise NoSuchBucketError(error)
            raise MinioError("Ooops", error)

    async def list_objects(self, bucket: str, **kwargs: Any) -> List[str]:
        try:
            return [
                obj.object_name
                for obj in await self.executor.run(
                    self.s3.list_objects, bucket, **kwargs
                )
            ]
        except S3Error as error:
            if error.code == "NoSuchBucket":
                raise NoSuchBucketError(error)
            raise MinioError("Ooops", error)

    async def object_exists(self, bucket: str, name: str, **kwargs: Any) -> bool:
        try:
            await self.executor.run(self.s3.stat_object, bucket, name, **kwargs)
        except S3Error as error:
            if error.code in ("NoSuchKey", "NoSuchBucket"):
                return False
            raise MinioError("Ooops", error)
        else:
            return True
