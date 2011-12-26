__all__ = ['assert_edges_equal']
from nose.tools import *

def assert_edges_equal(elist1,elist2):
    return assert_equal(sorted((sorted(e) for e in elist1)),
                        sorted((sorted(e) for e in elist2)))
