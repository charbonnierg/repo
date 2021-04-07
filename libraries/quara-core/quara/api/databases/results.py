from dataclasses import dataclass
from typing import List


@dataclass
class InsertOneResult:
    inserted_id: str


@dataclass
class InsertManyResult:
    inserted_ids: List[str]


@dataclass
class DeleteResult:
    deleted_count: int


@dataclass
class UpdateResult:
    modified_count: int


__all__ = ["DeleteResult", "InsertManyResult", "InsertOneResult", "UpdateResult"]
