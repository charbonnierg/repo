from quara.api.brokers import Message, Subject
from quara.api.brokers.dependencies import get_callback_params
from quara.core.types import JsonModel


def test_get_callback_params():
    """Test that callback parameters are injected properly."""

    async def cb(message: Message, subject: Subject, event: JsonModel):
        pass

    msg = Message(subject="test", data={}, context=None, reply=None)

    params = get_callback_params(cb, msg)
    event = params.get("event")
    subject = params.get("subject")
    message = params.get("message")
    assert event.dict() == {}
    assert message.subject == subject == "test"
    assert JsonModel(**message.data) == event
