from inspect import Parameter
from typing import Union, get_args, get_origin


def is_optional(param: Parameter) -> bool:
    return get_origin(param.annotation) is Union and type(None) in get_args(
        param.annotation
    )
