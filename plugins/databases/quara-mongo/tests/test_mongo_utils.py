# type: ignore[no-untyped-def]
import bson
import pytest
from bson.objectid import ObjectId
from quara.core.errors import InvalidDocumentId
from quara.databases.mongo.utils import (
    format_filter_ids,
    generate_filters,
    map_dict_to_documents,
    map_documents_to_dicts,
    str_to_bson_id,
)


@pytest.mark.mongo
def test_str_to_bson_id():
    """Test that:

    - object id can be reconstructed from string
    - bad string raises an error."""
    # Create stome object ID
    _id = bson.ObjectId()
    # The representation of an object ID can be reverted to an object ID
    assert str_to_bson_id(str(_id)) == _id
    # A bad value will raise an InvalidDocumentId error
    with pytest.raises(InvalidDocumentId):
        str_to_bson_id("bad_object_id")


@pytest.mark.mongo
def test_map_documents_to_dicts():
    """Test that an iterable of mongo documents have their "_id" field transform into "id" field."""
    # Create a list of documents
    docs = [{"_id": bson.ObjectId()}, {"_id": bson.ObjectId()}]
    # Convert toducments to dictionnaries, I.E, transform "_id" key in "id"
    dicts = map_documents_to_dicts(docs)
    # Assert that "id" key is present
    assert all(["id" in _dict for _dict in dicts])
    # Assert that "_id" is not present
    assert all(["_id" not in _dict for _dict in dicts])
    # Dicts can be converted back to documents
    assert map_dict_to_documents(dicts) == docs


@pytest.mark.mongo
def test_format_filter_id_str():
    """Test that string IDs are replaced with bson Object IDs."""
    objectid = ObjectId()
    strobjectid = str(objectid)
    _filter = format_filter_ids(strobjectid)
    assert _filter == {"$eq": objectid}


@pytest.mark.mongo
def test_format_filter_id_list_str():
    """Test that string IDs are replaced with bson Object IDs."""
    objectids = [ObjectId()]
    strobjectid = str(objectids[0])
    _filter = format_filter_ids([strobjectid])
    assert _filter == {"$in": objectids}


@pytest.mark.mongo
def test_format_filter_id_eq():
    """Test that string IDs are replaced with bson Object IDs."""
    objectid = ObjectId()
    strobjectid = str(objectid)
    _filter = format_filter_ids({"$eq": strobjectid})
    assert _filter == {"$eq": objectid}


@pytest.mark.mongo
def test_format_filter_id_in():
    """Test that string IDs are replaced with bson Object IDs."""
    objectids = [ObjectId()]
    strobjectid = str(objectids[0])
    _filter = format_filter_ids({"$in": [strobjectid]})
    assert _filter == {"$in": objectids}


@pytest.mark.mongo
def test_generate_filters():
    """Test that equality filters are generated from kwargs"""
    # Create an object id
    objectid = ObjectId()
    # Create some keyword arguments that should be transformed to mongo filters
    kwargs = dict(a=1, b=[1, 2, 3], c={"$in": [1, 2, 3]}, id=[objectid])
    # Generate filters
    f = generate_filters(**kwargs)
    # Since "a" is an integer, it should produce an equality filter by default
    assert f["a"] == {"$eq": 1}
    # Since "b" is an array, it should produce an equality filter by default
    assert f["b"] == {"$eq": [1, 2, 3]}
    # Since "c" is already a filter, it should be kept as is
    assert f["c"] == {"$in": [1, 2, 3]}
    # "id" filter should be removed in favor of "_id"
    assert "id" not in f
    # "_id" generates a "$in" filter by default when receiving an array
    # (it is impossible for an "_id" field to be equal to an array anyway)
    assert f["_id"] == {"$in": [objectid]}
