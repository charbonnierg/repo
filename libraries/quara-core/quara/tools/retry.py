from functools import wraps
from typing import Dict


# Since this is a decorator, we don't care about the return type
def retry(retries: int = 3):  # type: ignore
    """Decorator to make a function retriable."""
    left: Dict[str, int] = {"retries": retries}

    # We don't care about the type of the decorator function either
    def decorator(f):  # type: ignore
        # And finally decorated function gets all its annotations from original function f
        @wraps(f)
        def inner(*args, **kwargs):  # type: ignore
            while left["retries"]:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    print(e)
                    left["retries"] -= 1
                    print("Retries Left", left["retries"])
            raise Exception("Retried {} times".format(retries))

        return inner

    return decorator
