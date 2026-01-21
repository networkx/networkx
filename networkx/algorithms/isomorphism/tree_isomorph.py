"""
Tree isomorphism functions.
"""
import networkx as nx
from networkx.exception import NetworkXError

__author__ = """\n""".join(['Balazs Kossovics (kossovics@gmail.com)',
    'Jeffrey Finkelstein (jeffrey.finkelstein@gmail.com)'])

__all__ = ['rooted_tree_is_isomorphic',
           'tree_is_isomorphic']

# based on http://crypto.cs.mcgill.ca/~crepeau/CS250/2004/HW5+.pdf
#   and jfinkels' comment
# usage:
# T1 = nx.random_powerlaw_tree(10, tries=1000)
# T2 = nx.random_powerlaw_tree(10, tries=1000)
# print tree_is_isomorphic(T1, T2)

def canonical_form(T, root, _from=None):
    try:
        children = filter(lambda node: node != _from, T[root])
        if len(children) == 0:
            return ()
        return tuple(sorted(canonical_form(T, v, root) for v in children))
    except KeyError:
        raise NetworkXError("Graph {} contains no node {}".format(T, root))

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
    for r1 in nx.center(T1):
        if rooted_tree_is_isomorphic(T1, T2, r1, r2): 
            return True
    return False

