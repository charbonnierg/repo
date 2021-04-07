from typing import List, Optional

from pydantic import BaseSettings


class BrokerContext(BaseSettings):
    enabled: bool = True
    backend: str = "nats"
    host: str = "localhost"
    port: int = 4222
    tls: bool = False
    servers: Optional[List[str]] = None

    class Config:
        extra = "allow"
        case_sensitive = False
        env_prefix = "broker_"
