import sys
from copy import copy
from contextlib import ContextDecorator

__all__ = [
    "assert_nodes_equal",
    "assert_edges_equal",
    "assert_graphs_equal",
    "almost_equal",
    "missing_modules",
]


def almost_equal(x, y, places=7):
    return round(abs(x - y), places) == 0


def assert_nodes_equal(nodes1, nodes2):
    # Assumes iterables of nodes, or (node,datadict) tuples
    nlist1 = list(nodes1)
    nlist2 = list(nodes2)
    try:
        d1 = dict(nlist1)
        d2 = dict(nlist2)
    except (ValueError, TypeError):
        d1 = dict.fromkeys(nlist1)
        d2 = dict.fromkeys(nlist2)
    assert d1 == d2


def assert_edges_equal(edges1, edges2):
    # Assumes iterables with u,v nodes as
    # edge tuples (u,v), or
    # edge tuples with data dicts (u,v,d), or
    # edge tuples with keys and data dicts (u,v,k, d)
    from collections import defaultdict

    d1 = defaultdict(dict)
    d2 = defaultdict(dict)
    c1 = 0
    for c1, e in enumerate(edges1):
        u, v = e[0], e[1]
        data = [e[2:]]
        if v in d1[u]:
            data = d1[u][v] + data
        d1[u][v] = data
        d1[v][u] = data
    c2 = 0
    for c2, e in enumerate(edges2):
        u, v = e[0], e[1]
        data = [e[2:]]
        if v in d2[u]:
            data = d2[u][v] + data
        d2[u][v] = data
        d2[v][u] = data
    assert c1 == c2
    # can check one direction because lengths are the same.
    for n, nbrdict in d1.items():
        for nbr, datalist in nbrdict.items():
            assert n in d2
            assert nbr in d2[n]
            d2datalist = d2[n][nbr]
            for data in datalist:
                assert datalist.count(data) == d2datalist.count(data)


def assert_graphs_equal(graph1, graph2):
    assert graph1.adj == graph2.adj
    assert graph1.nodes == graph2.nodes
    assert graph1.graph == graph2.graph


class missing_modules(ContextDecorator):
    """
    Creates a decorator where the decorated (test) function will be run in a
    context simulating an environment where any module in `modules_to_remove`
    is not installed.

    The target use-case for this decorator is to test the raising of
    ImportError and ImportWarning.

    A usage example::

        @missing_modules(['numpy'])
        def test_raises_import_error():
            with pytest.raises(ImportError):
                import numpy as np

    In this example, `missing_modules` creates a context in which
    `test_raises_import_error` passes, regardless of whether `numpy` is
    installed on the target system.
    """

    def __init__(self, modules_to_remove):
        """
        Remove modules from local context.

        Parameters
        ----------
        modules_to_remove : list of strings
            A list of strings where each string is the name of a module to
            be removed from the local context, e.g. ['numpy', 'scipy']
        """

        if not isinstance(modules_to_remove, list):
            raise TypeError(
                "The argument to `missing_modules` must be a list of strings."
            )
        self._orig_sysmodules = copy(sys.modules)
        self._modules_to_remove = modules_to_remove

    def __enter__(self):
        for mod in self._modules_to_remove:
            # Causes ModuleNotFoundError, a subclass of ImportError
            sys.modules[mod] = None

    def __exit__(self, *exc):
        # Restore sys.modules when exiting context
        sys.modules.update(self._orig_sysmodules)
