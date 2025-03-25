import networkx as nx
from networkx.algorithms.chordal import complete_to_chordal_graph

def test_complete_to_chordal_graph():
    # Create a non-chordal graph (cycle of 4)
    G = nx.cycle_graph(4)  # Cycle Graph: 0 - 1 - 2 - 3 - 0 (not chordal)

    # Apply the function
    H, peo = complete_to_chordal_graph(G)

    # Ensure H is chordal
    assert nx.is_chordal(H), "Output graph is not chordal!"

    # Ensure peo is valid
    assert isinstance(peo, dict), "PEO should be a dictionary!"
    assert len(peo) == len(G.nodes()), "PEO should include all nodes!"

    # Ensure all original edges exist in H
    for u, v in G.edges():
        assert H.has_edge(u, v), f"Missing original edge ({u}, {v})"