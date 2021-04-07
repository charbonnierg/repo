from pydantic import BaseSettings
from pydantic.types import SecretStr


class StorageContext(BaseSettings):
    enabled: bool = True
    backend: str = "minio"
    host: str = "localhost"
    port: int = 9000
    access_key: str = "minioadmin"
    secret_key: SecretStr = SecretStr("minioadmin")
    secure: bool = False
    max_workers: int = 4

    class Config:
        extra = "allow"
        case_sensitive = False
        env_prefix = "storage_"
