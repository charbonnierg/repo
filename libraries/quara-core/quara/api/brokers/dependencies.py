"""This module is used by Broker Subscriptions to inject keyword arguments into subscription callbacks.

The only function exposed in the public API is `get_callback_params`.
"""

from functools import partial
from typing import Any, Callable, Dict, Type, get_type_hints

from pydantic import BaseModel

from .models import Message, Subject


def _check_pydantic_model(_type: Type[Any]) -> bool:
    """Check that given object is a valid pydantic model class."""
    try:
        return issubclass(_type, BaseModel)
    except TypeError:
        return False


def _get_model(_type: Type[BaseModel], msg: Message) -> BaseModel:
    """Get a pydantic model with given type from message."""
    if not msg.data:
        msg.data = {}
    return _type(**msg.data)


def _get_subject(msg: Message) -> Subject:
    """Extract subject from message."""
    return msg.subject


def _identity(msg: Message) -> Message:
    """Dummy _identity function."""
    return msg


def _get_callback_dependencies(
    function: Callable[..., Any],
) -> Dict[str, Callable[[Message], Any]]:
    """Identify callback arguments and return a dictionnary of keys
    and functions.

    Each function can be used to return argument value from
    message.
    """
    # Create an empty dict of params
    params: Dict[str, Callable[..., Any]] = {}
    type_hints = get_type_hints(function)
    # Get type hints for parameters
    iter_params = [
        (name, annotation)
        for name, annotation in type_hints.items()
        if name != "return"
    ]
    # Iterate over the parameters
    while iter_params:
        param_name, param_type = iter_params.pop(0)
        if param_type in (Subject, "Subject"):
            params[param_name] = _get_subject
        elif param_type in (Message, "Message"):
            params[param_name] = _identity
        elif _check_pydantic_model(param_type):
            get_model = partial(_get_model, param_type)
            params[param_name] = get_model

    return params


def get_callback_params(function: Callable[..., Any], msg: Message) -> Dict[str, Any]:
    """Extract dict of callback parameters names and values from message."""
    dependencies = _get_callback_dependencies(function)
    kwargs = {name: value(msg) for name, value in dependencies.items()}
    return kwargs


__all__ = ["get_callback_params"]
