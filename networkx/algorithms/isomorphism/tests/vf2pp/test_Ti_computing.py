import utils

import networkx as nx
from networkx.algorithms.isomorphism.vf2pp import _GraphParameters, _StateParameters
from networkx.algorithms.isomorphism.vf2pp_helpers.state import (
    _restore_Tinout,
    _update_Tinout,
)


class TestTinoutUpdating:
    V = 500
    G = nx.gnp_random_graph(V, 0.6, seed=24)

    # initialize empty mapping
    mapping = dict()
    reverse_mapping = dict()

    # initialize Ti/Ti_out
    T1 = set()
    T2 = set()
    T1_out = set(G.nodes())
    T2_out = set(G.nodes())

    def test_incremental_updating(self):
        # Check initialial conditions
        correct_T1, correct_T2, correct_T1_out, correct_T2_out = utils.compute_Ti(
            self.G, self.G, self.mapping, self.reverse_mapping
        )

        assert correct_T1 == self.T1
        assert correct_T2 == self.T2
        assert correct_T1_out == self.T1_out
        assert correct_T2_out == self.T2_out

        graph_params = _GraphParameters(self.G, self.G, None, None, None, None, None)
        state_params = _StateParameters(
            self.mapping,
            self.reverse_mapping,
            self.T1,
            self.T1_out,
            self.T2,
            self.T2_out,
        )

        # Gradually update the mapping until all nodes are mapped, and validate the Ti updating
        for node in self.G.nodes():
            self.mapping.update({node: node})
            self.reverse_mapping.update({node: node})

            correct_T1, correct_T2, correct_T1_out, correct_T2_out = utils.compute_Ti(
                self.G, self.G, self.mapping, self.reverse_mapping
            )
            _update_Tinout(node, node, graph_params, state_params)
            assert correct_T1 == self.T1
            assert correct_T2 == self.T2
            assert correct_T1_out == self.T1_out
            assert correct_T2_out == self.T2_out

    def test_restoring(self):
        # Create a dummy mapping
        self.mapping = {node: node for node in self.G.nodes()}
        self.reverse_mapping = {node: node for node in self.G.nodes()}

        # Initialize Ti/Ti_out
        self.T1, self.T2, self.T1_out, self.T2_out = utils.compute_Ti(
            self.G, self.G, self.mapping, self.reverse_mapping
        )

        graph_params = _GraphParameters(self.G, self.G, None, None, None, None, None)
        state_params = _StateParameters(
            self.mapping,
            self.reverse_mapping,
            self.T1,
            self.T1_out,
            self.T2,
            self.T2_out,
        )

        # Remove every node from the mapping one by one and verify the correct restoring of Ti/Ti_out
        for node in [key_node for key_node in self.mapping.keys()]:
            self.mapping.pop(node)
            self.reverse_mapping.pop(node)

            T1, T2, T1_out, T2_out = utils.compute_Ti(
                self.G, self.G, self.mapping, self.reverse_mapping
            )
            _restore_Tinout(node, node, graph_params, state_params)
            assert self.T1 == T1
            assert self.T2 == T2
            assert self.T1_out == T1_out
            assert self.T2_out == T2_out
