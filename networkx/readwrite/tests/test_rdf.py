# -*- coding: utf-8 -*-
"""
Unit tests for rdf.
"""
import io
import networkx
import networkx.readwrite.rdf as rdf
from networkx.exception import NetworkXError
from nose import SkipTest
from nose.tools import assert_equals, assert_raises, assert_true


class TestRdf():
    @classmethod
    def setupClass(cls):
        try:
            rdflib = rdf._rdflib()
        except ImportError:
            raise SkipTest('rdflib is not available')

    def setUp(self):
        self.simple_data = """<http://www.w3.org/2001/08/rdf-test/> <http://purl.org/dc/elements/1.1/creator>   "Dave Beckett" .
<http://www.w3.org/2001/08/rdf-test/> <http://purl.org/dc/elements/1.1/creator>   "Jan Grant" .
<http://www.w3.org/2001/08/rdf-test/> <http://purl.org/dc/elements/1.1/publisher> _:a .
_:a                                   <http://purl.org/dc/elements/1.1/title>     "World Wide Web Consortium" .
_:a                                   <http://purl.org/dc/elements/1.1/source>    <http://www.w3.org/> .
"""

        self.rgml_data = """<?xml version="1.0" encoding="utf-8"?>

<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns="http://purl.org/puninj/2001/05/rgml-schema#"
  xmlns:rgml="http://purl.org/puninj/2001/05/rgml-schema#">

<Graph rdf:ID="g1" rgml:directed="true">
   <nodes>
      <rdf:Bag>
         <rdf:li rdf:resource="#n1"/>
         <rdf:li rdf:resource="#n2"/>
      </rdf:Bag>
   </nodes>

   <edges>
      <rdf:Bag>
         <rdf:li rdf:resource="#e1"/>
      </rdf:Bag>
   </edges>
</Graph>

<Node rdf:ID="n1" rgml:weight="0.1" rgml:label="http://www.w3.org/Home/Lassila"/>
<Node rdf:ID="n2" rgml:weight="0.5" rgml:label="Ora Lassila"/>

<Edge rdf:ID="e1" rgml:weight="1">
    <source rdf:resource="#n1"/>
    <target rdf:resource="#n2"/>
</Edge>

</rdf:RDF>
"""

    def test_from_rgmlgraph(self):
        fh = io.BytesIO(self.rgml_data.encode('UTF-8'))
        fh.seek(0)

        rdflib = rdf._rdflib()
        G = rdflib.Graph()
        G.load(fh)

        assert_raises(NetworkXError,
                      networkx.from_rgmlgraph,
                      G,
                      namespace='this is not RGML')

        N = networkx.from_rgmlgraph(G)
        assert_true(N.is_directed(), 'Returns directed representation')
        assert_equals(len(N), 2, 'Number of nodes')
        assert_equals(len(N.edges()), 1, 'Number of edges')

        namespace = 'http://purl.org/puninj/2001/05/rgml-schema#'
        rgml = rdflib.Namespace(namespace)
        G.bind('rgml', str(rgml))

        # mixed graph
        graph_node = G.value(predicate=rdflib.RDF.type,
                             object=rgml.Graph,
                             any=False)
        G.add((graph_node, rgml.directed, rdflib.term.Literal(False)))
        G.add((graph_node, rgml.directed, rdflib.term.Literal(True)))
        with assert_raises(NetworkXError) as e:
            networkx.from_rgmlgraph(G)
        assert_equals(e.exception.message, 'from_rgmlgraph() does not support mixed graphs ', 'Mixed graph')
        G.remove((graph_node, rgml.directed, rdflib.term.Literal(False)))
        G.remove((graph_node, rgml.directed, rdflib.term.Literal(True)))

        # Nested graph
        graph_node = rdflib.term.BNode()
        G.add((graph_node, rdflib.RDF.type, rgml.Graph))
        with assert_raises(NetworkXError) as e:
            networkx.from_rgmlgraph(G)
        assert_equals(e.exception.message, 'from_rgmlgraph() does not support nested graphs ', 'Nested/multiple graphs')
        G.remove((graph_node, rdflib.RDF.type, rgml.Graph))

        # hypergraph
        hyperedge_node = rdflib.term.BNode()
        seq_node = rdflib.term.BNode()
        node1_node = rdflib.term.BNode()
        node2_node = rdflib.term.BNode()
        node3_node = rdflib.term.BNode()
        G.add((hyperedge_node, rgml.nodes, seq_node))
        G.add((seq_node, rdflib.RDF.li, node1_node))
        G.add((seq_node, rdflib.RDF.li, node2_node))
        G.add((seq_node, rdflib.RDF.li, node3_node))
        G.add((hyperedge_node, rdflib.RDF.type, rgml.Edge))
        G.add((node1_node, rdflib.RDF.type, rgml.Node))
        G.add((node2_node, rdflib.RDF.type, rgml.Node))
        G.add((node3_node, rdflib.RDF.type, rgml.Node))
        G.add((seq_node, rdflib.RDF.type, rdflib.RDF.Seq))
        with assert_raises(NetworkXError) as e:
            networkx.from_rgmlgraph(G)
        assert_equals(e.exception.message, 'from_rgml() does not support hypergraphs ', 'Hypergraphs')
        
    def test_from_rdfgraph(self):
        fh = io.BytesIO(self.simple_data.encode('UTF-8'))
        fh.seek(0)

        rdflib = rdf._rdflib()
        G = rdflib.Graph()
        G.load(fh, format='nt')

        assert_raises(NetworkXError,
                      networkx.from_rdfgraph,
                      G,
                      create_using=networkx.Graph())

        # bipartite representation
        N = networkx.from_rdfgraph(G, create_using=None)
        assert_true(networkx.bipartite.is_bipartite(N),
                    'Returns bipartite representation')

        statements = [n for n in N.nodes(data=True) if n[1]['bipartite'] == 0]
        nodes = [n for n in N.nodes(data=True) if n[1]['bipartite'] == 1]

        assert_equals(len(statements), 5, 'Number of statements')
        assert_equals(len(nodes), 10, 'Number of unique nodes')
        [assert_true(s[0][0] == 's',
                     'Correct statement node id prefix') for s in statements]
        [assert_true(n[0] in range(10), 'Correct node id') for n in nodes]

        # directed labeled multigraph representation
        N = networkx.from_rdfgraph(G, create_using=networkx.MultiDiGraph())
        assert_true(N.is_directed(), 'Returns directed representation')
        assert_true(N.is_multigraph(), 'Returns multigraph representation')

        nodes = N.nodes(data=True)

        assert_equals(len(nodes), 6, 'Number of unique nodes')
        [assert_true(n[0] in range(10), 'Correct node id') for n in nodes]

    def test_to_rdfgraph(self):
        fh = io.BytesIO(self.simple_data.encode('UTF-8'))
        fh.seek(0)

        rdflib = rdf._rdflib()
        G = rdflib.Graph()
        G.load(fh, format='nt')

        # bipartite representation
        N = networkx.from_rdfgraph(G, create_using=None)
        G1 = networkx.to_rdfgraph(N)
        assert_true(G.isomorphic(G1), 'Isomorphic round-trip bipartite conversion.')
        
        # directed labeled multigraph representation
        N = networkx.from_rdfgraph(G, create_using=networkx.MultiDiGraph())
        G1 = networkx.to_rdfgraph(N)
        assert_true(G.isomorphic(G1), 'Isomorphic round-trip multigraph conversion.')

        # generic graph representation
        N = networkx.barabasi_albert_graph(100, 1, 0)
        N.label = 'RGML Graph'
        for n in N:
            N.node[n]['label'] = n
            N.node[n]['weight'] = n
            N.node[n]['some other attribute'] = n
        for i, (u, v) in enumerate(N.edges()):
            N.edge[u][v]['label'] = i
            N.edge[u][v]['weight'] = i
            N.edge[u][v]['some other attribute'] = i
        G1 = networkx.to_rdfgraph(N)
        assert_true('rgml' in [str(x[0]) for x in G1.namespaces()],
                    'NetworkX generated graph in RGML namespace')
        
    def test_read_rdf(self):
        fh = io.BytesIO(self.simple_data.encode('UTF-8'))
        fh.seek(0)

        assert_raises(NetworkXError,
                      networkx.read_rdf,
                      fh,
                      fmt='does not exist')

        assert_true(type(networkx.read_rdf(fh,
                                           create_using=None,
                                           fmt='nt')) is networkx.Graph,
                    'Returns NetworkX graph')


    def test_write_rdf(self):
        fh=io.BytesIO()
        networkx.write_rdf(networkx.barabasi_albert_graph(100,1,0), fh, fmt='n3')
        fh.seek(0)
        assert_true(isinstance(networkx.read_rdf(fh, fmt='n3'),
                               networkx.Graph),
                    'Roundtrip NX <-> RDF in N3 format')

        assert_raises(NetworkXError,
                      networkx.write_rdf,
                      networkx.barabasi_albert_graph(100, 1, 0),
                      fh,
                      fmt='does not exist')

    def test_read_rgml(self):
        fh = io.BytesIO(self.rgml_data.encode('UTF-8'))
        fh.seek(0)

        assert_raises(NetworkXError,
                      networkx.read_rgml,
                      fh,
                      fmt='does not exist')

        N = networkx.read_rdf(fh, create_using=None)
        assert_true(type(N) is networkx.Graph, 'Returns NetworkX graph')
        
    def test_write_rgml(self):
        fh=io.BytesIO()
        networkx.write_rgml(networkx.barabasi_albert_graph(100,1,0), fh, fmt='n3')
        fh.seek(0)

        assert_raises(NetworkXError,
                      networkx.write_rgml,
                      networkx.barabasi_albert_graph(100, 1, 0),
                      fh,
                      fmt='does not exist')
        fh.seek(0)

        assert_true(isinstance(networkx.read_rgml(fh, fmt='n3'),
                               networkx.Graph),
                    'Roundtrip NX <-> RDF in N3 format')

    def test__relabel(self):
        N = networkx.Graph()
        N.add_nodes_from([(0, {'label':'a'}), (1, {'label':'a'})])
        assert_raises(NetworkXError,
                      rdf._relabel,
                      N)

    def test__rdflib(self):
        try:
            import builtins
        except ImportError:
            import __builtin__ as builtins

        realimport = builtins.__import__

        def myimport(a, b, c, d):
            raise ImportError
        builtins.__import__ = myimport
        assert_raises(ImportError, rdf._rdflib)
        builtins.__import__ = realimport
