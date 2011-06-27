"""
    Specific VF2 implementation for graphs with weights.
    The user can also specify a node_match function.
"""

import sys
import networkx as nx

from .vf2userfunc import GraphMatcher, DiGraphMatcher

__all__ = ['WeightedGraphMatcher',
           'WeightedDiGraphMatcher',
           'WeightedMultiGraphMatcher',
           'WeightedMultiDiGraphMatcher']

def weight_factory(weight, default, rtol, atol, multi):
    """
    Returns a function which compares the `weight` attributes of edges.

    Parameters
    ----------
    weight : str
        An edge attribute.
    default : float
        The default value to use if an edge has no `weight` attribute.
    rtol : float
        The relative tolerance used to compare weights.
    atol : float
        The absolute tolerance used to compare weights.
    multi : bool
        If `True`, the a weight function is constructed that is suitable for
        multigraphs and multidigraphs. Otherwise, the function is suitable
        for graphs and digraphs only.

    Returns
    -------
    weight_match : callable
        A function which compares the `weight` attribute of edges.

    """
    if weight is None:
        weight_match = None

    elif multi:
        def weight_match(g1_edges, g2_edges):
            # We sort the weights and make sure they are close elementwise.
            data1 = sorted([d.get(weight,default) for d in g1_edges.values()])
            data2 = sorted([d.get(weight,default) for d in g2_edges.values()])
            for x,y in zip(data1,data2):
                if not abs(x-y) <= atol + rtol * abs(y):
                    return False
            return True

    else:
        def weight_match(e1_attrs, e2_attrs):
            w1 = e1_attrs.get(weight, default)
            w2 = e2_attrs.get(weight, default)
            # assumes finite weights
            if abs(w1-w2) <= atol + rtol * abs(w2):
                return True
            else:
                return False

    return weight_match

def init_factory(cls, multi):
    """
    Returns an __init__ function, specialied for (di)graphs and multi(di)graphs.

    Parameters
    ----------
    cls : class
        The class whose __init__ method is being constructed.
    multi : bool
        If `True`, then the class is meant to work with multigraphs.

    Returns
    -------
    __init__ : callable
        An __init__ function customized to the class and whether or not it is
        meant to work with multigraphs.

    """
    def __init__(self, G1, G2, node_match=None, weight='weight', default=1,
                               rtol=1.0000000000000001e-05, atol=1e-08):
        """
        Initializes the graph matcher.

        Parameters
        ----------
        G1, G2 : graph
            The graphs to be tested.

        node_match : callable
            A function that returns True iff node `n1` in `G1` and `n2` in `G2`
            should be considered equal during the isomorphism test. The
            function will be called like:

               node_match(G1.node[n1], G2.node[n2])

            That is, the function will receive the node attribute dictionaries
            of the nodes under consideration. If `None`, then no attributes are
            considered when testing for an isomorphism.

        weight : str
            The edge attribute used during the isomorphism check. The value
            of the edge attribute must act like a float.

        default : float
            If an edge does not have the `weight` parameter, then `default`
            will be used as the default value.

        rtol : float
            The relative tolerance used when comparing floats.

        atol : float
            The absolute tolerance used when comparing floats.

        See Also
        --------
        :mod:`networkx.algorithms.isomorphism.vf2userfunc`

        """
        edge_match = weight_factory(weight, default, rtol, atol, multi=multi)
        super(cls, self).__init__(G1, G2, node_match, edge_match)

    return __init__


# Programmatically create all the classes
classes = [ ('WeightedGraphMatcher', (GraphMatcher,), False),
            ('WeightedDiGraphMatcher', (DiGraphMatcher,), False),
            ('WeightedMultiGraphMatcher', (GraphMatcher,), True),
            ('WeightedMultiDiGraphMatcher', (DiGraphMatcher,), True), ]
this = sys.modules[__name__]
method = '__init__'
for className, baseClasses, multi in classes:
    cls = type(className, baseClasses, {})
    setattr(this, className, cls)
    setattr(cls, method, init_factory(cls, multi))


