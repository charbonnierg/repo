"""Utilities functions for MongoDB connectors."""
from typing import Any, Dict, Iterable, Iterator, List, Union

import bson
from quara.core.errors import InvalidDocumentId


def str_to_bson_id(_id: str) -> bson.ObjectId:
    """Take a string and return a bson.ObjectId."""
    try:
        return bson.ObjectId(_id)
    except bson.errors.InvalidId as err:
        raise InvalidDocumentId(err)


def str_to_bson_ids_generator(iterable: Iterable[str]) -> Iterator[bson.ObjectId]:
    """Take an iterable of IDs as string and return a generator of bson Object IDs."""
    return (str_to_bson_id(_id) for _id in iterable)


def map_str_to_bson_ids(iterable: Iterable[str]) -> List[bson.ObjectId]:
    """Take an iterable of IDs as string and return a list of bson Object IDs."""
    return list(str_to_bson_ids_generator(iterable))


def sanitize_document_id(document: Dict[str, Any]) -> Dict[str, Any]:
    """Take a dictionnary as argument and return the same dictionnary with "id" key instead of "_id"."""
    doc = document.copy()
    try:
        doc["id"] = str(doc.pop("_id"))
    except KeyError:
        pass
    return doc


def sanitized_id_documents_generator(
    iterable: Iterable[Dict[str, Any]]
) -> Iterator[Dict[str, Any]]:
    """Take an iterable of bson documents as dictionnaries and return an iterable of dictionnaries."""
    return (sanitize_document_id(document) for document in iterable)


def map_documents_to_dicts(iterable: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Take a list of documents and return a list of documents with IDs as string."""
    return list(sanitized_id_documents_generator(iterable))


def dict_to_document(_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Take a dictionnary as argument, look for the "id" key and replace it with "_id" as bson ID."""
    __dict = _dict.copy()
    try:
        __dict["_id"] = str_to_bson_id(__dict.pop("id"))
    except KeyError:
        pass
    return __dict


def dicts_to_documents_generator(
    iterable: Iterable[Dict[str, Any]]
) -> Iterator[Dict[str, Any]]:
    return (dict_to_document(_dict) for _dict in iterable)


def map_dict_to_documents(iterable: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return list(dicts_to_documents_generator(iterable))


def format_filter_ids(_id: Union[str, List[str], Dict[str, Any]]) -> Dict[str, Any]:
    """Format id filter."""
    _filter: Dict[str, Any] = dict()
    # Let's consider a fitler is a dictionnary when it has a "key" method
    try:
        keys: List[str] = _id.keys()  # type: ignore
    except AttributeError:
        # Let's check if it's a list
        if isinstance(_id, list):
            return {"$in": map_str_to_bson_ids(_id)}
        else:
            # In this case we must expect a string
            __filter: str = _id  # type: ignore
            return {"$eq": str_to_bson_id(__filter)}
    else:
        # In this case it's indeed a dictionnary. Something like {"$eq": <str>]} or {"$in": <List[str]>}
        for key in keys:
            # Let's try to cast a string to bson ID
            try:
                _filter[key] = str_to_bson_id(_id[key])  # type: ignore
            # If it fails due to a type error [TypeError: id must be an instance of (bytes, str, ObjectId), not <class '...'>]
            except TypeError:
                # We can only try to consider the value as an iterable
                _filter[key] = map_str_to_bson_ids(_id[key])  # type: ignore
    # Once we iterated over all keys we can return the filter
    return _filter


def generate_filters(**kwargs: Any) -> Dict[str, Any]:
    """Generate equality filter to use with MongoDB."""
    # Generate empty filter dictionnary
    filters = dict()
    # If we get a keyword argument named "id"
    _id = kwargs.pop("id", None)
    # Let's handle all other kwargs
    for key, filter in kwargs.items():
        # Here it's hard to duck type, we don't need a particular method
        if isinstance(filter, dict):
            filters[key] = filter
        # If it's not a dict we construct the dict ourself
        else:
            filters[key] = {"$eq": filter}
    # To ensure all IDs are valid Object IDs
    if _id:
        # We can use the "format_filter_ids"
        filters["_id"] = format_filter_ids(_id)
    # Once we iterator over all keys we can return the filters
    return filters
