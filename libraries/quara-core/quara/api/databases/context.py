from pydantic import BaseSettings


class DatabaseContext(BaseSettings):
    enabled: bool = True
    backend: str = "mongo"
    host: str = "localhost"
    port: int = 27017
    name: str = "test"
    timeout: int = 5

    class Config:
        extra = "allow"
        case_sensitive = False
        env_prefix = "database_"
