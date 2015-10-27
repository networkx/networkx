"""
Tree isomorphism functions.
"""
import networkx as nx
from networkx.exception import NetworkXError

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')


import matplotlib
import matplotlib.pyplot
import matplotlib.pyplot as plt

__author__ = """\n""".join(['Balazs Kossovics (kossovics@gmail.com)',
    'Jeffrey Finkelstein (jeffrey.finkelstein@gmail.com)'])

__all__ = ['rooted_tree_is_isomorphic',
           'tree_is_isomorphic']




def canonical_form(T, root, _from=None):
    children = filter(lambda node: node != _from, T.neighbors(root))
    if len(children) == 0:
        return ()
    return tuple(sorted(canonical_form(T, v, root) for v in children))

def rooted_tree_is_isomorphic(T1, T2, r1, r2):
    if not nx.is_tree(T1):
        raise NetworkXError("Graph {} is not a tree.".format(T1))

    if not nx.is_tree(T2):
        raise NetworkXError("Graph {} is not a tree.".format(T2))

    return canonical_form(T1, r1) == canonical_form(T2, r2)


def tree_is_isomorphic(T1, T2):
    if not T2:
        return not T1

    r2 = nx.center(T2)[0]
    print "first", T2, "center", r2
    for r1 in nx.center(T1):
        print "second", T1, "center", r1
        if rooted_tree_is_isomorphic(T1, T2, r1, r2): 
            return True
    return False
