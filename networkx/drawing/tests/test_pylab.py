"""Unit tests for matplotlib drawing functions."""
import os
import itertools
import pytest

mpl = pytest.importorskip("matplotlib")
mpl.use("PS")
plt = pytest.importorskip("matplotlib.pyplot")
plt.rcParams["text.usetex"] = False

import networkx as nx


class TestPylab:
    @classmethod
    def setup_class(cls):
        cls.G = nx.barbell_graph(4, 6)

    def test_draw(self):
        try:
            functions = [
                nx.draw_circular,
                nx.draw_kamada_kawai,
                nx.draw_planar,
                nx.draw_random,
                nx.draw_spectral,
                nx.draw_spring,
                nx.draw_shell,
            ]
            options = [{"node_color": "black", "node_size": 100, "width": 3}]
            for function, option in itertools.product(functions, options):
                function(self.G, **option)
                plt.savefig("test.ps")

        finally:
            try:
                os.unlink("test.ps")
            except OSError:
                pass

    def test_draw_shell_nlist(self):
        try:
            nlist = [list(range(4)), list(range(4, 10)), list(range(10, 14))]
            nx.draw_shell(self.G, nlist=nlist)
            plt.savefig("test.ps")
        finally:
            try:
                os.unlink("test.ps")
            except OSError:
                pass

    def test_edge_colormap(self):
        colors = range(self.G.number_of_edges())
        nx.draw_spring(
            self.G, edge_color=colors, width=4, edge_cmap=plt.cm.Blues, with_labels=True
        )
        # plt.show()

    def test_arrows(self):
        nx.draw_spring(self.G.to_directed())
        # plt.show()

    def test_edge_colors_and_widths(self):
        pos = nx.circular_layout(self.G)
        for G in (self.G, self.G.to_directed()):
            nx.draw_networkx_nodes(G, pos, node_color=[(1.0, 1.0, 0.2, 0.5)])
            nx.draw_networkx_labels(G, pos)
            # edge with default color and width
            nx.draw_networkx_edges(
                G, pos, edgelist=[(0, 1)], width=None, edge_color=None
            )
            # edges with global color strings and widths in lists
            nx.draw_networkx_edges(
                G, pos, edgelist=[(0, 2), (0, 3)], width=[3], edge_color=["r"]
            )
            # edges with color strings and widths for each edge
            nx.draw_networkx_edges(
                G, pos, edgelist=[(0, 2), (0, 3)], width=[1, 3], edge_color=["r", "b"]
            )
            # edges with fewer color strings and widths than edges
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(1, 2), (1, 3), (2, 3), (3, 4)],
                width=[1, 3],
                edge_color=["g", "m", "c"],
            )
            # edges with more color strings and widths than edges
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(3, 4)],
                width=[1, 2, 3, 4],
                edge_color=["r", "b", "g", "k"],
            )
            # with rgb tuple and 3 edges - is interpreted with cmap
            nx.draw_networkx_edges(
                G, pos, edgelist=[(4, 5), (5, 6), (6, 7)], edge_color=(1.0, 0.4, 0.3)
            )
            # with rgb tuple in list
            nx.draw_networkx_edges(
                G, pos, edgelist=[(7, 8), (8, 9)], edge_color=[(0.4, 1.0, 0.0)]
            )
            # with rgba tuple and 4 edges - is interpretted with cmap
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(9, 10), (10, 11), (10, 12), (10, 13)],
                edge_color=(0.0, 1.0, 1.0, 0.5),
            )
            # with rgba tuple in list
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(9, 10), (10, 11), (10, 12), (10, 13)],
                edge_color=[(0.0, 1.0, 1.0, 0.5)],
            )
            # with color string and global alpha
            nx.draw_networkx_edges(
                G, pos, edgelist=[(11, 12), (11, 13)], edge_color="purple", alpha=0.2
            )
            # with color string in a list
            nx.draw_networkx_edges(
                G, pos, edgelist=[(11, 12), (11, 13)], edge_color=["purple"]
            )
            # with single edge and hex color string
            nx.draw_networkx_edges(G, pos, edgelist=[(12, 13)], edge_color="#1f78b4f0")

            # edge_color as numeric using vmin, vmax
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(7, 8), (8, 9)],
                edge_color=[0.2, 0.5],
                edge_vmin=0.1,
                edge_vmax=0.6,
            )

            # plt.show()

    def test_labels_and_colors(self):
        G = nx.cubical_graph()
        pos = nx.spring_layout(G)  # positions for all nodes
        # nodes
        nx.draw_networkx_nodes(
            G, pos, nodelist=[0, 1, 2, 3], node_color="r", node_size=500, alpha=0.75
        )
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=[4, 5, 6, 7],
            node_color="b",
            node_size=500,
            alpha=[0.25, 0.5, 0.75, 1.0],
        )
        # edges
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[(0, 1), (1, 2), (2, 3), (3, 0)],
            width=8,
            alpha=0.5,
            edge_color="r",
        )
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[(4, 5), (5, 6), (6, 7), (7, 4)],
            width=8,
            alpha=0.5,
            edge_color="b",
        )
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[(4, 5), (5, 6), (6, 7), (7, 4)],
            min_source_margin=0.5,
            min_target_margin=0.75,
            width=8,
            edge_color="b",
        )
        # some math labels
        labels = {}
        labels[0] = r"$a$"
        labels[1] = r"$b$"
        labels[2] = r"$c$"
        labels[3] = r"$d$"
        labels[4] = r"$\alpha$"
        labels[5] = r"$\beta$"
        labels[6] = r"$\gamma$"
        labels[7] = r"$\delta$"
        nx.draw_networkx_labels(G, pos, labels, font_size=16)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=None, rotate=False)
        nx.draw_networkx_edge_labels(G, pos, edge_labels={(4, 5): "4-5"})
        # plt.show()

    def test_axes(self):
        fig, ax = plt.subplots()
        nx.draw(self.G, ax=ax)

    def test_empty_graph(self):
        G = nx.Graph()
        nx.draw(G)

    def test_draw_empty_nodes_return_values(self):
        # See Issue #3833
        from matplotlib.collections import PathCollection, LineCollection

        G = nx.Graph([(1, 2), (2, 3)])
        DG = nx.DiGraph([(1, 2), (2, 3)])
        pos = nx.circular_layout(G)
        assert isinstance(nx.draw_networkx_nodes(G, pos, nodelist=[]), PathCollection)
        assert isinstance(nx.draw_networkx_nodes(DG, pos, nodelist=[]), PathCollection)

        # drawing empty edges either return an empty LineCollection or empty list.
        assert isinstance(
            nx.draw_networkx_edges(G, pos, edgelist=[], arrows=True), LineCollection
        )
        assert isinstance(
            nx.draw_networkx_edges(G, pos, edgelist=[], arrows=False), LineCollection
        )
        assert isinstance(
            nx.draw_networkx_edges(DG, pos, edgelist=[], arrows=False), LineCollection
        )
        assert nx.draw_networkx_edges(DG, pos, edgelist=[], arrows=True) == []

    def test_multigraph_edgelist_tuples(self):
        # See Issue #3295
        G = nx.path_graph(3, create_using=nx.MultiDiGraph)
        nx.draw_networkx(G, edgelist=[(0, 1, 0)])
        nx.draw_networkx(G, edgelist=[(0, 1, 0)], node_size=[10, 20, 0])

    def test_alpha_iter(self):
        pos = nx.random_layout(self.G)
        # with fewer alpha elements than nodes
        plt.subplot(131)
        nx.draw_networkx_nodes(self.G, pos, alpha=[0.1, 0.2])
        # with equal alpha elements and nodes
        num_nodes = len(self.G.nodes)
        alpha = [x / num_nodes for x in range(num_nodes)]
        colors = range(num_nodes)
        plt.subplot(132)
        nx.draw_networkx_nodes(self.G, pos, node_color=colors, alpha=alpha)
        # with more alpha elements than nodes
        alpha.append(1)
        plt.subplot(133)
        nx.draw_networkx_nodes(self.G, pos, alpha=alpha)

    def test_error_invalid_kwds(self):
        with pytest.raises(ValueError, match="Received invalid argument"):
            nx.draw(self.G, foo="bar")

    def test_np_edgelist(self):
        # see issue #4129
        np = pytest.importorskip("numpy")
        nx.draw_networkx(self.G, edgelist=np.array([(0, 2), (0, 3)]))
