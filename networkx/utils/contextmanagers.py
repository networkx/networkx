from __future__ import absolute_import

from contextlib import contextmanager

__all__ = [
    'reversed',
]

@contextmanager
def reversed(G):
    """A context manager for temporarily reversing a directed graph in place.

    This is a no-op for undirected graphs.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    """
    directed = G.is_directed()
    if directed:
        G.reverse(copy=False)

    try:
        yield
    finally:
        if directed:
            # Reverse the reverse.
            G.reverse(copy=False)
