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

__all__ = ['read_rdf', 'from_rdfgraph', 'write_rdf', 'to_rdfgraph',
           'read_rgml', 'from_rgmlgraph']

import networkx as nx
from networkx.exception import NetworkXError


def _rdflib():
    try:
        import rdflib
    except ImportError:
        raise ImportError('_get_rdflib_plugins() requires rdflib ',
                          'https://github.com/RDFLib/rdflib ')
    return rdflib


def _get_rdflib_plugins(kind):
    """Return list of strings corresponding to parsers or serializers
    accepted by rdflib.
    """
    rdflib = _rdflib()
    return [p.name for p in rdflib.plugin.plugins() if p.kind is kind]


def _make_elements(G, kind, **kwargs):
    """Given rdflib graph `G`, rdflib class `kind`, and namespace
    keywords `**kwargs`, return dict of dicts with keys objects of class
    `kind`, and values dicts of attributes obtained from triples where
    the key objects appear as subjects, and consisting of the respective
    predicates as keys and objects as values.

    """
    elements = {}
    for (e, k, v) in G.query("""SELECT DISTINCT ?element ?key ?value
     WHERE {
    ?element rdf:type ?kind.
    ?element ?key ?value.
    }""",
                             initNs={'rgml': kwargs['rgml'],
                                     'rdf': kwargs['rdf']},
                             initBindings={'kind': kind}):
        if k == kwargs['rdf'].type:
            continue
        elif k == kwargs['rgml'].label:
            k = 'label'
            v = str(v)
        elif k == kwargs['rgml'].weight:
            k = 'weight'
            v = float(v)

        if e in elements:
            elements[e][k] = v
        else:
            elements[e] = {k: v}

    return elements


def _relabel(G):
    """Relabel nodes in G with 'label' attributes if no duplicate node
    labels exist.
    """
    mapping = [(n, d['label'] if 'label' in d else n)
               for n, d in G.node.items()]
    x, y = zip(*mapping)
    if len(set(y)) != len(G):
        raise NetworkXError('Failed to relabel nodes: '
                            'duplicate node labels found. '
                            'Use relabel=False.')

    return nx.relabel_nodes(G, dict(mapping))


def _from_bipartite(N):
    """Reconstruct previously imported RDF graph G from bipartite
    representation N.
    """
    rdflib = _rdflib()
    G = rdflib.Graph(identifier=N.name)
    nodes = N.nodes_iter(data=True)
    for statement in [x[0] for x in nodes if not x[-1].get('bipartite')]:
        terms = dict([(N.edge[statement][x]['term'],
                       N.node[x]['label']) for x in N.edge[statement]])
        G.add((terms['subject'], terms['predicate'], terms['object']))
    return G


def _from_multigraph(N):
    """Reconstruct previously imported RDF graph G from directed labeled
    multigraph representation N.
    """
    rdflib = _rdflib()
    G = rdflib.Graph(identifier=N.name)

    # I think we don't need to consider disconnected nodes, since that
    # is impossible to represent in straight RDF. That is, RDF has a
    # concept of disconnected triples, but not terms, which are
    # properly analogous to nodes in networkx

    for s, o, p in N.edges_iter(data=True):
        _subject = N.node[s]['label']
        _object = N.node[o]['label']
        _predicate = p['label']
        G.add((_subject, _predicate, _object))
    return G


def to_rgmlgraph(N):
    """Return an rdflib RGML graph from a NetworkX graph.

    Parameters
    ----------
    G : NetworkX Graph
      A graph created with networkx

    """
    rdflib = _rdflib()
    G = rdflib.Graph(identifier=N.name)
    namespace = 'http://purl.org/puninj/2001/05/rgml-schema#'
    rgml = rdflib.Namespace(namespace)
    G.bind('rgml', str(rgml))
    G.bind('', '#')

    name = repr(N)

    graph_node = rdflib.term.Literal(name)
    edges_node = rdflib.term.BNode()
    nodes_node = rdflib.term.BNode()

    # add graph and its properties
    G.add((graph_node, rdflib.RDF.type, rgml.Graph))
    G.add((graph_node, rgml.edges, edges_node))
    G.add((graph_node, rgml.nodes, nodes_node))
    G.add((graph_node, rgml.directed, rdflib.term.Literal(N.is_directed())))
    label = getattr(N, 'label', False)
    if label:
        G.add((graph_node, rgml.label, rdflib.term.Literal(label)))

    # add nodes and their properties
    G.add((nodes_node, rdflib.RDF.type, rdflib.RDF.Bag))
    for n, attrs in N.nodes_iter(data=True):
        node = n
        if not isinstance(node, rdflib.term.Identifier):
            node = rdflib.term.URIRef('#{}'.format(n))
        G.add((nodes_node, rdflib.RDF.li, node))
        G.add((node, rdflib.RDF.type, rgml.Node))
        for k, v in _parse_attrs(attrs, rgml, rdflib):
            G.add((node, k, v))

    # add edges and their properties
    G.add((edges_node, rdflib.RDF.type, rdflib.RDF.Bag))
    for u, v, attrs in N.edges_iter(data=True):
        edge = (u, v)
        if not isinstance(edge, rdflib.term.Identifier):
            edge = rdflib.term.URIRef('#{}'.format(hash((u, v))))
        G.add((edges_node, rdflib.RDF.li, edge))
        G.add((edge, rdflib.RDF.type, rgml.Edge))
        G.add((edge, rgml.source, rdflib.term.URIRef('#{}'.format(u))))
        G.add((edge, rgml.target, rdflib.term.URIRef('#{}'.format(v))))
        for k, v in _parse_attrs(attrs, rgml, rdflib):
            G.add((edge, k, v))

    return G


def _parse_attrs(attrs, rgml, rdflib):
    for k, v in attrs.iteritems():
        if k == 'weight':
            k = rgml.weight
            v = rdflib.term.Literal(float(v))
        elif k == 'label':
            k = rgml.label
            v = rdflib.term.Literal(str(v))
        else:
            k = rdflib.term.URIRef('#{}'.format(k))
            v = rdflib.term.Literal(v)
        yield k, v

        
def from_rgmlgraph(G, namespace='http://purl.org/puninj/2001/05/rgml-schema#',
                   relabel=True):
    """Return a NetworkX graph from an rdflib RGML graph.

    Parameters
    ----------
    G : rdflib Graph
      A graph created with rdflib

    namespace : string, optional
      Alternative RGML namespace

    relabel : bool, optional
      If True use the RGML node label attribute for node names,
      otherwise use the rdflib object itself.

    Notes
    -----
    This implementation does not support mixed graphs (directed and
    unidirected edges together), hyperedges, or nested graphs.

    The namespace as typically published in RGML documents is
    http://purl.org/puninj/2001/05/rgml-schema#, which points to
    http://www.cs.rpi.edu/~puninj/RGML/, but the RGML schema currently
    resides at
    http://www.cs.rpi.edu/research/groups/pb/punin/public_html/RGML/.

    """
    rdflib = _rdflib()
    if namespace not in [str(x[1]) for x in G.namespaces()]:
        raise NetworkXError('from_rgmlgraph() requires an RGML-namespaced graph ',
                            namespace)

    rdf = rdflib.RDF
    rgml = rdflib.Namespace(namespace)
    G.bind('rgml', str(rgml))

    try:
        graph_lit = G.value(predicate=rdf.type, object=rgml.Graph, any=False)
    except rdflib.exceptions.UniquenessError:
        raise NetworkXError('from_rgmlgraph() does not support nested graphs ')

    try:
        directed = G.value(subject=graph_lit, predicate=rgml.directed)
    except rdflib.exceptions.UniquenessError:
        raise NetworkXError('from_rgmlgraph() does not support mixed graphs ')

    hyperedges = G.query("""SELECT DISTINCT ?edge
    WHERE {
    ?edge rgml:nodes ?seq .
    ?seq  ?predicate ?node .
    ?node rdf:type   rgml:Node .
    ?edge rdf:type   rgml:Edge .
    ?seq  rdf:type   rdf:Seq .
    }""", initNs=dict(rgml=rgml, rdf=rdf))

    if len(hyperedges):
        raise NetworkXError('from_rgml() does not support hypergraphs')

    # assign defaults
    create_using = nx.Graph()
    if directed:
        create_using = nx.DiGraph()
    N = nx.empty_graph(0, create_using)
    N.name = G.identifier

    # add nodes with attributes
    for node, attrs in _make_elements(G, rgml.Node, rdf=rdf,
                                      rgml=rgml).iteritems():
        N.add_node(node, attrs)

    # add edges with attributes source and target come as predicates
    # from the _make_elements call, so we need to pop them out of the
    # dict before creating the edge proper.
    for edge, attrs in _make_elements(G, rgml.Edge, rdf=rdf,
                                      rgml=rgml).iteritems():
        source = attrs[rgml.source]
        target = attrs[rgml.target]
        del attrs[rgml.source]
        del attrs[rgml.target]
        if 'label' not in attrs:
            attrs['label'] = edge
        N.add_edge(source, target, attrs)

    if relabel:
        N = _relabel(N)

    return N


def read_rgml(path, format='xml', relabel=True):
    """Return a NetworkX graph from an RGML rdf file on path.

    Parameters
    ----------
    path : file or string
       File name or file handle or url to read.

    format : string, optional
       RDFlib parser to use ({})

    relabel : bool, optional
      If True use the RGML node label attribute for node names,
      otherwise use the rdflib object itself.

    See from_rgmlgraph() for details.

    """
    rdflib = _rdflib()
    read_rdf.__doc__.format(_get_rdflib_plugins(rdflib.parser.Parser))

    G = rdflib.Graph()
    G.load(path, format=format)
    return from_rgmlgraph(G, relabel)


def write_rgml(N, path, format='xml'):
    """Write N in RGML RDF/format to path

    Parameters
    ----------
    N : graph
       A networkx graph
    path : file or string
       File or filename to write.
    format :
       RDFlib serializer to use ({})

    Examples
    --------
    >>> N=nx.path_graph(4)
    >>> nx.write_rgml(N, "test.rdf")

    Notes
    -----
    This implementation does not support mixed graphs (directed and
    unidirected edges together), hyperedges, or nested graphs.

    See to_rgmlgraph() for details.
    """
    rdflib = _rdflib()
    write_rdf.__doc__.format(_get_rdflib_plugins(rdflib.serializer.Serializer))

    G = to_rgmlgraph(N)
    G.serialize(path, format=format)
    return G


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
    >>> G=nx.from_rdfgraph(A)

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
                                 [_subject, _object, _predicate],
                                 [{'term': t} for t in ['subject',
                                                        'object',
                                                        'predicate']]))
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
    rdflib = _rdflib()
    read_rdf.__doc__.format(_get_rdflib_plugins(rdflib.parser.Parser))

    G = rdflib.Graph()
    G.load(path, format=format)
    return from_rdfgraph(G, create_using)


def to_rdfgraph(N):
    """Return an rdflib graph from a NetworkX graph N.

    Parameters
    ----------
    N : NetworkX graph
      A graph created with NetworkX

    Examples
    --------
    >>> K5 = nx.complete_graph(5)
    >>> G = nx.to_rdfgraph(K5)

    Notes
    -----

    If all nodes and edges in N have a 'label' key in their attribute
    dict with rdflib.term.Identifier values, an rdflib graph will be
    constructed with those terms instead of the node IDs.

    If the nodes in N have a 'bipartite' key in their attribute dict
    with values 0 and 1, and the edges in N have a 'term' key pointing
    to values in ['subject', 'object', 'predicate'], an rdflib graph
    will be constructed from triples corresponding to each node in
    partition 0, each built from the respective subject, predicate, and
    object nodes in partition 1.

    If the above fail, then we generate an RGML graph.
    """
    rdflib = _rdflib()
    nodes = N.nodes_iter(data=True)
    edges = N.edges_iter(data=True)

    nodes_bipartite = iter([x[-1].get('bipartite') for x in nodes])
    edges_terms = iter([x[-1].get('term') for x in edges])

    nodes_labels = iter([x[-1].get('label') for x in nodes])
    edges_labels = iter([x[-1].get('label') for x in edges])

    if all([x for x in nodes_bipartite if x]) \
       and all([x in [0, 1] for x in nodes_bipartite]) \
       and all([x in ['subject', 'object', 'predicate'] for x in edges_terms]):

        return _from_bipartite(N)

    elif all(nodes_labels) and all(edges_labels) \
        and all([isinstance(x,
                            rdflib.term.Identifier) for x in nodes_labels]) \
        and all([isinstance(x,
                            rdflib.term.Identifier) for x in edges_labels]):

        return _from_multigraph(N)

    else:
        return to_rgmlgraph(N)


def write_rdf(N, path, format='xml'):
    """Write N in RDF/format to path

    Parameters
    ----------
    N : graph
       A networkx graph
    path : file or string
       File or filename to write.
    format :
       RDFlib serializer to use ({})

    Examples
    --------
    >>> N=nx.path_graph(4)
    >>> nx.write_rdf(N, "test.rdf")

    Notes
    -----
    This implementation does not support mixed graphs (directed and
    unidirected edges together), hyperedges, or nested graphs.

    See to_rdfgraph() for details.
    """
    rdflib = _rdflib()
    write_rdf.__doc__.format(_get_rdflib_plugins(rdflib.serializer.Serializer))

    G = to_rdfgraph(N)
    G.serialize(format=format)
    return G
