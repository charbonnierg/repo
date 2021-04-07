from inspect import signature
from typing import Optional

import pytest
from quara.core.params import is_optional


@pytest.mark.core
def test_is_optional():
    def f(a: Optional[int]):
        pass

    s = signature(f)
    for name, param in s.parameters.items():
        assert is_optional(param)

    def f2(a: int):
        pass

    s2 = signature(f2)
    for name, param in s2.parameters.items():
        assert not is_optional(param)
