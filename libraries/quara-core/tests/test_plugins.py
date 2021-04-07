from typing import Any

import pytest
from quara.core.plugins import Pluggable


@pytest.mark.core
def test_bad_plugin():
    # Define a child class of Pluggable
    class MyPluggableAPI(Pluggable[Any]):
        # Do NOT define a __default_backend__ class attribute
        pass

    with pytest.raises(ValueError):
        # An error should be raised
        MyPluggableAPI()
