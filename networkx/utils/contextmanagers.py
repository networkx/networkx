from __future__ import absolute_import

from contextlib import contextmanager

__all__ = [
    'reversed',
]

@contextmanager
def reversed(G):
    """
    A context manager for temporarily reversing a directed graph.

    This is a no-op for undirected graphs.

    Parameters
    ----------
    G : graph
        A NetworkX graph
    copy : bool
        If True, then a new graph is returned. If False, then the graph is
        reversed in place.

    Returns
    -------
    H : graph
        The reversed G.

    """
    copy = False
    directed = G.is_directed()
    if directed:
        H = G.reverse(copy=copy)
    else:
        H = G

    try:
        yield H
    finally:
        if directed:
            # Reverse the reverse.
            H.reverse(copy=copy)
