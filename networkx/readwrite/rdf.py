# -*- coding: utf-8 -*-
"""
*******
RDF
*******
Read and write graphs in RDF format.

"RDF is a standard model for data interchange on the Web. RDF has
features that facilitate data merging even if the underlying schemas
differ, and it specifically supports the evolution of schemas over time
without requiring all the data consumers to be changed.

RDF extends the linking structure of the Web to use URIs to name the
relationship between things as well as the two ends of the link (this is
usually referred to as a 'triple'). Using this simple model, it allows
structured and semi-structured data to be mixed, exposed, and shared
across different applications.

This linking structure forms a directed, labeled graph, where the edges
represent the named link between two resources, represented by the graph
nodes. This graph view is the easiest possible mental model for RDF and
is often used in easy-to-understand visual explanations."

https://www.w3.org/RDF/

Requires rdflib: https://github.com/RDFLib/rdflib

Serialization formats
---------------------
All serialization formats supported by `rdflib` are supported, currently::

* RDF/XML (http://www.w3.org/TR/rdf-syntax-grammar/)
* Notation 3 (http://www.w3.org/TeamSubmission/n3/)
* Turtle (http://www.w3.org/TeamSubmission/turtle/)
* N-Triples (http://www.w3.org/TR/rdf-testcases/#ntriples)
* Trix (https://www.hpl.hp.com/techreports/2004/HPL-2004-56)

"""

__author__ = """Pedro Silva (psilva+git@pedrosilva.pt)"""
#    Copyright (C) 2013 by
#    Pedro Silva <psilva+git@pedrosilva.pt>
#    All rights reserved.
#    BSD license.

__all__ = ['read_rdf', 'from_rdfgraph', 'to_rdfgraph', 'write_rdf']

import networkx as nx
from networkx.exception import NetworkXError


def _get_rdflib_plugins(kind):
    try:
        import rdflib
    except ImportError:
        raise ImportError('_get_rdflib_plugins() requires rdflib ',
                          'https://github.com/RDFLib/rdflib ')
    return [p.name for p in rdflib.plugin.plugins() if p.kind is kind]


def from_rdfgraph(G, create_using=None):
    """Return a NetworkX MultiDiGraph or (bipartite) Graph from an
    rdflib Graph.

    Parameters
    ----------
    G : rdflib Graph
      A graph created with rdflib

    create_using : NetworkX graph class instance
      The output is created using the given graph class instance

    Examples
    --------
    >>> K5=nx.complete_graph(5)
    >>> A=nx.to_rdfgraph(K5)
    >>> G=nx.from_rdfgraphf(A)

    Notes
    -----
    The default representation, returned when `create_using` is None is
    a bipartite graph, in which case the graph G will be an undirected
    graph with two sets of nodes: one set for RDF statements (the
    hyperedges), and one set for the actual triples (one node for each
    subject, predicate, and object). Each statement edge connects its
    respective triple.

    If `create_using` is passed as a Multi(Di)Graph, then we proceed
    with a (un)directed labeled multigraph, in which case the graph will
    possibly contain multiple reifications of the same entity, occurring
    both as edge (predicate) and as node (subject or object).

    References
    ----------
    Hayes, J. (2004). A graph model for RDF. Technische Universität
    Darmstadt. Retrieved from
    http://www.dcc.uchile.cl/~cgutierr/papers/rdfgraphmodel.pdf
    """
    if create_using is not None and not create_using.is_multigraph():
        raise NetworkXError('RDF graph model requires a multigraph',
                            '''(s, p, o) followed by (s, p', o) is valid RDF
     and implies repeated edges between s and o''')

    # assign defaults
    N = nx.empty_graph(0, create_using)
    N.name = G.identifier

    # `node_keys` is a dict with monotonic integers as keys and rdflib
    # objects as values. `start` is an offset for new rdflib objects
    # indices computed through the second enumerate, below
    nodes = G.all_nodes() | set(G.predicates())
    node_keys = dict([reversed(n) for n in (enumerate(nodes))])
    offset = len(nodes)

    # populate the nx graph: Because RDF terms are pretty verbose, and
    # to closely follow Hayes (2004), nodes are simple integers, and the
    # rdflib objects themselves are stored under the 'label' attribute
    for n, (s, p, o) in enumerate(G, start=offset):

        # If the same rdflib object occurs more than once, its key is
        # retrieved from the node_keys structure initialized above
        _subject = node_keys.get(s, n)
        _object = node_keys.get(o, n+offset)
        _predicate = node_keys.get(p, n+offset*2)
        _statement = 's%d' % (n-offset)

        # bipartite branch
        if create_using is None:
            N.add_node(_statement, bipartite=0)
            N.add_node(_subject, label=s, bipartite=1)
            N.add_node(_object, label=o, bipartite=1)
            N.add_node(_predicate, label=p, bipartite=1)
            N.add_edges_from(zip([_statement]*3,
                                 [_subject, _object, _predicate]))
        # directed labeled multigraph branch
        else:
            N.add_node(_subject, label=s)
            N.add_node(_object, label=o)
            N.add_edge(_subject, _object, label=p)

    return N


def read_rdf(path, format='xml', create_using=None):
    """Return a NetworkX MultiDiGraph or (bipartite) Graph from an rdf
    file on path.

    Parameters
    ----------
    path : file or string
       File name or file handle or url to read.

    format : string
       RDFlib parser to use ({})

    See from_rdfgraph() for details.
    """
    try:
        import rdflib
    except ImportError:
        raise ImportError('read_rdf() requires rdflib ',
                          'https://github.com/RDFLib/rdflib ')
    read_rdf.__doc__.format(_get_rdflib_plugins(rdflib.parser.Parser))

    G = rdflib.Graph()
    G.load(path, format=format)
    return from_rdfgraph(G, create_using)
