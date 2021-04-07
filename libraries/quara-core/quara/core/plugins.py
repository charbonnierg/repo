from abc import ABC
from typing import Any, Generic, Optional, Type, TypeVar

from loguru import logger
from pkg_resources import iter_entry_points

from .errors import PluginImportFailedError, PluginNotFoundError


def load_plugin(name: str, group: str) -> Any:
    """Load a plugin by name for a given group."""
    # Try to load the plugin
    try:
        plugin = next(
            resource for resource in iter_entry_points(group) if resource.name == name
        )
    # a StopIteration is raised if the plugin does not exist
    except StopIteration:
        # In this case we raise an error
        logger.debug(f"Available plugins: {list(iter_entry_points(group))}")
        raise PluginNotFoundError(f"plugin '{name}' does not exist in group: '{group}'")
    try:
        return plugin.load()
    except Exception as err:
        raise PluginImportFailedError(
            f"plugin {name} failed to load with error: {str(err)}", error=err
        )


T = TypeVar("T", bound=Any)


class Pluggable(Generic[T]):
    """A base class for classes supporting plugin backends."""

    __group__: str
    __default_backend__: str

    def __init__(self, backend: Optional[str] = None, /, **kwargs: Any) -> None:
        """Create a new database client instance."""
        if not backend:
            try:
                backend = self.__default_backend__
            except AttributeError:
                raise ValueError(
                    "You must specify which backend to use as first positional argument."
                )
        backend_factory: Type[T] = load_plugin(backend, self.__group__)
        self._backend: T = backend_factory(**kwargs)


class Plugin(ABC):
    pass
