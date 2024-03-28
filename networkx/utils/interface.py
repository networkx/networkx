from abc import abstractmethod
from collections.abc import Callable
from importlib.metadata import entry_points
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    TypedDict,
    TypeVar,
    runtime_checkable,
)

from networkx.exception import NetworkXException

if TYPE_CHECKING:
    from importlib.metadata import EntryPoint

    import pytest

    import networkx as nx


G = TypeVar("G")


class BackendRegistrationException(ImportError, NetworkXException):
    ...


class BackendInfo(TypedDict, total=False):
    backend_name: str
    functions: dict[str, dict[str, Any]]
    short_summary: str


@runtime_checkable
class BackendInterface(Generic[G], Protocol):
    @classmethod
    @abstractmethod
    def convert_from_nx(
        cls,
        G: "nx.Graph",
        edge_attrs: dict[str, Any] | None,
        node_attrs: dict[str, Any] | None,
        preserve_edge_attrs: bool,  # are these optional?
        preserve_node_attrs: bool,
        preserve_graph_attrs: bool,
        preserve_all_attrs: bool,
        name: str,
        graph_name: str,
    ) -> G:
        ...

    @classmethod
    @abstractmethod
    def convert_to_nx(cls, result: G, name: str | None) -> "nx.Graph":
        ...

    @classmethod
    def can_run(cls, name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> bool:
        ...

    @classmethod
    def on_start_tests(cls, items: "list[pytest.Item]") -> None:
        ...

    def __init_subclass__(
        cls,
        plugin: bool = False,
        info: bool = False,
        fallback: Callable[[str], Callable[..., Any]] | None = None,
        **kw,
    ) -> None:  # unsure on var names here
        super().__init_subclass__(**kw)

        missing_methods = []
        for required_method in BackendInterface.__abstractmethods__:
            # option to check optional methods exist too?
            if not hasattr(cls, required_method):
                missing_methods.append(required_method)
        if missing_methods:
            raise BackendRegistrationException(
                "Backend missing required methods: "
                + ", ".join(f"`{name}`" for name in missing_methods)
            )

        if not plugin and info:
            raise BackendRegistrationException(
                "Unable to check backend info without plugin entrypoint"
            )

        if plugin:
            name = _get_entry_point(cls, group="networkx.backends").name
            if info:
                info_factory = _get_entry_point(
                    name, group="networkx.backend_info"
                ).load()
                if not callable(info_factory):
                    raise BackendRegistrationException(
                        "Invalid type returned by 'networkx.backend_info' entrypoint "
                        f"(expected callable, got {type(info_factory)})."
                    )
                _info = info_factory()
                if _info["backend_name"] != name:
                    raise BackendRegistrationException(
                        "Backend registered under different name than given in backend information"
                    )
                _check_networkx_api(cls, _info)

        if fallback is not None:
            setattr(type(cls), "__getattr__", staticmethod(fallback))


def _get_entry_point(
    select: str | type[BackendInterface], /, *, group: str
) -> "EntryPoint":
    if isinstance(select, str):
        name = f"'{select}'"
        eps = iter(entry_points(group=group, name=select))
    else:
        value = f"{select.__module__}:{select.__qualname__}"
        name = f"interface '{select.__qualname__}'"
        eps = iter(entry_points(group=group, value=value))

    ep = next(eps, None)
    if ep is None:
        raise BackendRegistrationException(
            f"Backend {name} did not register a '{group}' entry point."
        )
    if next(eps, None) is not None:
        # raise BackendRegistrationException(
        #     f"Backend '{name}' registered multiple '{group}' entry points."
        # )
        # warn otherwise LoopbackDispatcher raises this exception
        import warnings

        warnings.warn(
            f"Backend {name} registered multiple '{group}' entry points.",
            RuntimeWarning,
        )
    return ep


def _check_networkx_api(interface, backend_info: BackendInfo) -> None:
    import networkx.utils.backends

    for name in backend_info["functions"]:
        if not hasattr(interface, name):
            raise BackendRegistrationException(
                "Function declared in backend info not implemented by interface."
            )
        if name not in networkx.utils.backends._registered_algorithms:
            raise BackendRegistrationException(
                f"Unknown/undispatchable NetworkX function '{name}' registered by backend."
            )
