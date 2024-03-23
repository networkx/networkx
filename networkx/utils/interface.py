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
    import pytest

    import networkx as nx


G = TypeVar("G")


class BackendRegistrationException(ImportError, NetworkXException):
    ...


class BackendInfo(TypedDict, total=False):
    backend_name: str
    functions: dict[str, dict[str, Any]]


@runtime_checkable
class BackendInterface(Generic[G], Protocol):  # Type param for backend graph type?
    @abstractmethod
    def convert_from_nx(
        self,  # should these methods have self or be static (isinstance vs issubclass)?
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

    @abstractmethod
    def convert_to_nx(self, result: G, name: str) -> "nx.Graph":  # optional type?
        ...

    def can_run(self, name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> bool:
        ...

    def on_start_tests(self, items: "list[pytest.Item]") -> None:
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
            # option to check all methods?
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
            name = _get_backend_entry_point_name(cls)
            if info:
                _info = _get_backend_info(name)
                if _info["backend_name"] != name:
                    raise BackendRegistrationException(
                        "Backend info registered under different name than given in backend information"
                    )
                _check_networkx_api(cls, _info)

        if fallback is not None:
            setattr(type(cls), "__getattr__", staticmethod(fallback))


def _get_backend_entry_point_name(interface: type[BackendInterface]) -> str:
    expected_ep_value = f"{interface.__module__}:{interface.__qualname__}"
    eps = [
        ep
        for ep in entry_points(group="networkx.backends")
        if ep.value == expected_ep_value
    ]

    if not eps:
        raise BackendRegistrationException("Backend did not register an entry point")
    if len(eps) > 1:
        # raise BackendRegistrationException("Backend entry point defined multiple times")
        # warn because the LoopbackDispatcher would throw this error
        import warnings

        warnings.warn("Backend entry point defined multiple times", RuntimeWarning)
    return eps.pop().name


def _get_backend_info(name: str) -> BackendInfo:
    info_factory = next(
        iter(entry_points(group="networkx.backend_info", name=name)), None
    )
    # multiple times error/warning like with networkx.backends?
    if info_factory is None:
        raise BackendRegistrationException("Backend registered no information")
    if not callable(info_factory):
        raise BackendRegistrationException(
            "Invalid type returned by `backend_info` entrypoint"
        )
    return info_factory()


def _check_networkx_api(interface, backend_info: BackendInfo) -> None:
    import networkx.utils.backends

    for name in backend_info["functions"]:
        if not hasattr(interface, name):
            raise BackendRegistrationException(
                "Function declared in backend info not implemented by interface"
            )
        if name not in networkx.utils.backends._registered_algorithms:
            raise BackendRegistrationException("Unknown function registered by backend")
