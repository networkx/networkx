__all__ = ['assert_edges_equal']
from nose.tools import *

def assert_edges_equal(elist1,elist2):
    if len(elist1[0]) == 2:
        return assert_equal(set(tuple(sorted(e)) for e in elist1),
                            set(tuple(sorted(e)) for e in elist2))
    else:
        return assert_equal(sorted((sorted((u, v)), d) for u, v, d in elist1),
                            sorted((sorted((u, v)), d) for u, v, d in elist2))
