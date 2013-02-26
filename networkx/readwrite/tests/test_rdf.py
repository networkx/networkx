# -*- coding: utf-8 -*-
"""
Unit tests for rdf.
"""
import io
import networkx
from networkx.exception import NetworkXError
from nose import SkipTest
from nose.tools import assert_equals, assert_raises, assert_true


class TestRdf():
    @classmethod
    def setupClass(cls):
        try:
            import rdflib
        except ImportError:
            raise SkipTest('rdflib not available.')

    def setUp(self):
        self.simple_data = """<http://www.w3.org/2001/08/rdf-test/> <http://purl.org/dc/elements/1.1/creator>   "Dave Beckett" .
<http://www.w3.org/2001/08/rdf-test/> <http://purl.org/dc/elements/1.1/creator>   "Jan Grant" .
<http://www.w3.org/2001/08/rdf-test/> <http://purl.org/dc/elements/1.1/publisher> _:a .
_:a                                   <http://purl.org/dc/elements/1.1/title>     "World Wide Web Consortium" .
_:a                                   <http://purl.org/dc/elements/1.1/source>    <http://www.w3.org/> .
"""

    def test_from_rdfgraph(self):
        fh = io.BytesIO(self.simple_data.encode('UTF-8'))
        fh.seek(0)

        try:
            import rdflib
        except ImportError:
            raise SkipTest('rdflib not available.')

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

    def test_read_rdf(self):
        try:
            import rdflib
        except ImportError:
            raise SkipTest('rdflib not available.')

        fh = io.BytesIO(self.simple_data.encode('UTF-8'))
        fh.seek(0)

        assert_raises(rdflib.plugin.PluginException,
                      networkx.read_rdf,
                      fh,
                      format='does not exist')

        assert_true(type(networkx.read_rdf(fh,
                                           create_using=None,
                                           format='nt')) is networkx.Graph,
                    'Returns NetworkX graph')
