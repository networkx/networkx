from __future__ import absolute_import

from nose.tools import *

import networkx as nx

def test_reversed():
    G = nx.DiGraph()
    G.add_edge('A', 'B')

    # no exception
    with nx.utils.reversed(G) as H:
        pass
    assert_true('B' in G['A'])

    # exception
    try:
        with nx.utils.reversed(G) as H:
            raise Exception
    except:
        assert_true('B' in G['A'])
