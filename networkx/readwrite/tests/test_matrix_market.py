"""
Pajek tests
"""
import networkx as nx
import os
import tempfile
from networkx.utils import nodes_equal, edges_equal


class TestMatrixMarket:
    @classmethod
    def setup_class(cls):
        cls.data = (
            "%%MatrixMarket matrix coordinate pattern "
            "symmetric\n%-------------------------------------------------------------------------------\n% "
            "SuiteSparse Matrix Collection, Tim Davis\n% https://sparse.tamu.edu/Mycielski/mycielskian2\n% "
            "name: Mycielski/mycielskian2\n% [Mycielskian graph M2]\n% id: 2758\n% date: 2018\n% author: J. "
            "Mycielski\n% ed: S. Kolodziej\n% fields: title A name id date author ed kind notes\n% kind: "
            "undirected "
            "graph\n%-------------------------------------------------------------------------------\n% "
            "notes:\n% Mycielskian graph M2.\n%\n% The Mycielskian graph sequence generates graphs that are "
            "triangle-free\n% and with a known chromatic number (i.e. the minimum number of colors\n% required "
            "to color the vertices of the graph).\n%\n% Known properties of this graph (M2) include the "
            "following:\n%\n%  * M2 has a minimum chromatic number of 2.\n%  * M2 is triangle-free (i.e. no "
            "cycles of length 3 exist).\n%  * M2 has a Hamiltonian cycle.\n%  * M2 has a clique number of "
            "2.\n%  * M2 is factor-critical, meaning every subgraph of |V|-1 vertices has\n%    a perfect "
            "matching.\n%\n% Mycielski graphs were first described by Jan Mycielski in the following\n% "
            "publication:\n%\n%     Mycielski, J., 1955. Sur le coloriage des graphes. Colloq. Math.,"
            "\n%     3: "
            "161-162.\n%\n%-------------------------------------------------------------------------------\n2 "
            "2 1\n2 1 "
        )
        cls.G = nx.Graph()
        cls.G.add_nodes_from([0, 1])
        cls.G.add_edges_from([(0, 1)])

        cls.G.graph["name"] = "Tralala"
        (fd, cls.fname) = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as fh:
            fh.write(cls.data.encode("UTF-8"))

    @classmethod
    def teardown_class(cls):
        os.unlink(cls.fname)

    def test_read_mtx(self):
        import io

        mtx = io.StringIO(self.data)
        G = nx.read_mtx(mtx)
        assert sorted(G.nodes()) == [0, 1]
        assert edges_equal(
            G.edges(),
            [
                (0, 1),
            ],
        )

    def test_write_mtx(self):
        import io

        fh = io.BytesIO()
        nx.write_mtx(self.G, fh)
        fh.seek(0)
        fh = io.StringIO(str(fh.read().decode("utf-8")))
        H = nx.read_mtx(fh)
        assert nodes_equal(list(self.G), list(H))
        assert edges_equal(list(self.G.edges()), list(H.edges()))
