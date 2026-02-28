import networkx as nx


class ManyComponentsBenchmark:
    """Use atlas6() as a benchmarking case to probe for performance on graphs
    with many connected components.

    ``atlas6()`` is all of the graphs with at most 6 nodes and at least one edge
    that are connected and not isomorphic to one another (142 components in total).
    See the atlas6 gallery example for more info.
    """

    def setup(self):
        atlas = nx.graph_atlas_g()[
            3:209
        ]  # 0, 1, 2 => no edges. 208 is last 6 node graph
        U = nx.Graph()
        for G in atlas:
            if (nx.number_connected_components(G) == 1) and (
                not nx.isomorphism.GraphMatcher(U, G).subgraph_is_isomorphic()
            ):
                U = nx.disjoint_union(U, G)
        self.G = U

    def time_single_source_all_shortest_paths(self):
        _ = dict(nx.single_source_all_shortest_paths(self.G, 500))
