from dataclasses import dataclass
from functools import wraps
from importlib.metadata import entry_points


def dispatch(algo):
    def algorithm(func):
        @wraps(func)
        def wrapper(*args, **kwds):
            graph = args[0]
            plugins = entry_points(group="networkx.plugins")
            if isinstance(graph, WrappedGraph) and plugins:
                if isinstance(graph, WrappedSparse) and "sparse" in plugins.names:
                    backend = plugins["sparse"].load()
                    return getattr(backend, algo).__call__(*args, **kwds)
            return func(*args, **kwds)

        return wrapper

    return algorithm


@dataclass
class WrappedGraph:
    ...


@dataclass
class WrappedSparse(WrappedGraph):
    sparse_array: ...
    nodelist: list
