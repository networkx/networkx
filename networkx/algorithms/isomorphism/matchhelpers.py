"""
    Various functions which help end users define customize node_match and 
    edge_match functions to use during isomorphism checks.
"""

__all__ = ['close',
           'attrcompare_factory',
           'multi_attrcompare_factory_setlike'
          ]


def close(x, y, rtol=1.0000000000000001e-05, atol=1e-08):
    """Returns True if x and y are sufficiently close.

    Parameters
    ----------
    rtol : float
        The relative error tolerance.
    atol : float
        The absolute error tolerance.

    """
    # assumes finite weights
    return abs(x-y) <= atol + rtol * abs(y)

def attrcompare_factory(attrs):
    """Returns a customized attribute comparison function.

    For each attribute, the comparison functions are logically ANDed together.
    The comparison function is suitable as a `node_match` function or as an
    `edge_match` function for non-multi graphs and non-multi digraphs.

    Parameters
    ----------
    attrs : dict
        A dictionary keyed by attributes. The values should be 2-tuples of the
        form: (operator, default) where `operator` is the operator that should
        be used to compare the attribute values and `default` is the deafult
        value to use if an attribute does not exist in the dictionary.

    Returns
    -------
    match : callable
        A customized match function that can be used in (di)graph matchers.

    Examples
    --------
    >>> from networkx.algorithms.isomorphism.vf2userfunc import close
    >>> from operator import eq
    >>> attrs = { 'color': (eq, ''),
    ...           'size':  (close, 10),
    ...           'shape': (eq, 'circle') }
    ...
    >>> match = attrcompare_factory(attrs)
    >>> # g1 and g2 can be any graph or digraph, multi or not
    >>> gm = nx.is_isomorphic(g1, g2, node_match=match)
    >>> # g1 and g2 can be any non-multi graph or non-multi digraph
    >>> gm = nx.is_isomorphic(g1, g2, edge_match=match)

    """
    # We perform the logical AND of the operators.
    def match(attrs_g1, attrs_g2):
        for attr, (op, default) in attrs.items():
            v1 = attrs_g1.get(attr, default)
            v2 = attrs_g2.get(attr, default)
            if not op(v1, v2):
                return False
        else:
            return True

    return match

def multi_attrcompare_factory_setlike(attrs):
    """Returns a customized attribute comparison function for multi(di)graphs.

    For each attribute in `attrs`, a set of tuples is built from all the edges
    in each dictionary of dictionary of edge attributes. The comparison
    function is suitable as an `edge_match` function for multigraphs and
    multidigraphs.

    Parameters
    ----------
    attrs : dict
        A dictionary keyed by attributes. The values should be the default
        attribute values to use when an edge does not have the attribute
        specified.  The values of each edge attribute are assumed to be
        hashable and comparable via the == operator.

    Returns
    -------
    match : callable
        A customized match function that can be used in multi(di)graph matchers.

    Examples
    --------
    >>> from networkx.algorithms.isomorphism.vf2userfunc import close
    >>> from operator import eq
    >>> attrs = { 'color': '',
    ...           'linewidth': 10,
    ...           'shape': 'circle' }
    ...
    >>> match = multi_attrcompare_factory_setlike(attrs)
    >>> # g1 and g2 are multigraphs or multidigraphs
    >>> gm = nx.is_isomorphic(g1, g2, edge_match=match)

    """
    def match(attrs_g1, attrs_g2):
        data1 = set([])
        for eattrs in attrs_g1.values():
            x = tuple( eattrs.get(attr, d) for attr, d in attrs.items() )
            data1.add(x)
        data2 = set([])
        for eattrs in attrs_g2.values():
            x = tuple( eattrs.get(attr, d) for attr, d in attrs.items() )
            data2.add(x)

        return data1 == data2

    return match

