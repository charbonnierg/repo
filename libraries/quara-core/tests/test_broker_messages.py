import pytest
from quara.api import Message
from quara.core.errors import InvalidMessageDataError, InvalidMessageError


def test_invalid_message() -> None:
    class MissingOriginData:
        pass

    with pytest.raises(InvalidMessageError):
        Message.from_raw_msg(MissingOriginData())

    class BadOriginData:
        data = "already decoded"

    with pytest.raises(InvalidMessageError):
        Message.from_raw_msg(BadOriginData())

    class NotJSONOriginData:
        data = b'{object: "Not JSON"}'

    with pytest.raises(InvalidMessageError):
        Message.from_raw_msg(NotJSONOriginData())

    class NoSubject:
        data = b'{"test": "valid JSON"}'

    with pytest.raises(InvalidMessageError):
        Message.from_raw_msg(NoSubject())

    class InvalidOriginData:
        subject = "test"
        data = b'{"__context__": "something"}'

    with pytest.raises(InvalidMessageDataError):
        Message.from_raw_msg(InvalidOriginData())

    class ValidOriginMessage:
        subject = "test"
        data = b'{"__context__": {"traceparent": "test"}, "__data__": {}}'

    message = Message.from_raw_msg(ValidOriginMessage())
    assert message.subject == "test"
    assert message.reply == ""
    assert message.data == {}

    class ValidOriginMessageListData:
        subject = "test"
        data = b'{"__context__": {"traceparent": "test"}, "__data__": []}'

    message = Message.from_raw_msg(ValidOriginMessageListData())
    assert message.subject == "test"
    assert message.reply == ""
    assert message.data == []
