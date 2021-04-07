from pydantic import BaseSettings


class SchedulerContext(BaseSettings):
    enabled: bool = True
    backend: str = "apscheduler"

    class Config:
        extra = "allow"
        case_sensitive = False
        env_prefix = "scheduler_"
