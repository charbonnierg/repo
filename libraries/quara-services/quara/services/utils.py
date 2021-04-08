from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import Query, Request
from fastapi.param_functions import Depends


def get_query_filters_from_request(
    request: Request,
    limit: Optional[int] = Query(None, ge=1),
    offset: Optional[int] = Query(None, ge=0),
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Get query parameters related to database query operations."""
    # Create an empty dictionnary
    params: Dict[str, Any] = dict()
    # Update the dictionnary with all keys and values found in request query parameters
    params.update(request.query_params)
    # Remove the "from_date" param
    params.pop("from_date", None)
    # Remove the "to_date" param
    params.pop("to_date", None)
    # Remove None values
    if limit is None:
        params.pop("limit", None)
    if offset is None:
        params.pop("offset", None)
    # Create a mongodb-like filter expression
    # And assign it to the "timestamp" param
    if from_date and to_date:
        # Both start and end dates were given
        params["timestamp"] = {"$gte": from_date, "$lte": to_date}
    elif from_date:
        # Only start date was given
        params["timestamp"] = {"$gte": from_date}
    elif to_date:
        # Only end date was given
        params["timestamp"] = {"$lte": to_date}
    return params


QueryFilters = Depends(get_query_filters_from_request)
