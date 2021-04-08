from typing import Any, Dict, List

from pydantic import BaseModel


class InsertionResponse(BaseModel):
    id: str


class MultipleInsertionResponse(BaseModel):
    ids: List[str]


class CountResponse(BaseModel):
    count: int


class HTTPErrorMessage(BaseModel):
    details: str
    error: str


HTTP_400_BAD_REQUEST: Dict[int, Dict[str, Any]] = {
    400: {"description": "Request error", "model": HTTPErrorMessage}
}

HTTP_403_FORBIDDEN: Dict[int, Dict[str, Any]] = {
    403: {"description": "Action forbidden", "model": HTTPErrorMessage}
}

HTTP_404_NOT_FOUND: Dict[int, Dict[str, Any]] = {
    404: {"description": "Resource not found", "model": HTTPErrorMessage}
}

HTTP_409_CONFLICT: Dict[int, Dict[str, Any]] = {
    409: {"description": "Resource already exists", "model": HTTPErrorMessage}
}

HTT_500_INTERNAL_ERROR: Dict[int, Dict[str, Any]] = {
    500: {"description": "Internal server error", "model": HTTPErrorMessage}
}

WS_OBJECT_NOT_FOUND: int = 4004
WS_GATEWAY_NOT_REACHABLE: int = 4005
