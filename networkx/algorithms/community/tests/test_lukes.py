import networkx as nx
from networkx.algorithms.community import lukes_clustering

EWL = 'e_weight'
NWL = 'n_weight'


# first test from the Lukes original paper
def test_paper_1():

    limit = 3
    ground_truth = {frozenset([1, 4]),
                    frozenset([2, 3, 5])}

    example_1 = nx.Graph()

    example_1.add_edge(1, 2, **{EWL: 3})
    example_1.add_edge(1, 4, **{EWL: 2})
    example_1.add_edge(2, 3, **{EWL: 4})
    example_1.add_edge(2, 5, **{EWL: 6})

    nx.set_node_attributes(example_1, 1, NWL)

    clusters_1 = {frozenset(x) for x in lukes_clustering(example_1, limit, node_weight=NWL, edge_weight=EWL)}

    assert clusters_1 == ground_truth


# second test from the Lukes original paper
def test_paper_2():

    byte_block_size = 32
    ground_truth = {frozenset(['education', 'bs', 'ms', 'phd']),
                    frozenset(['name', 'home_address']),
                    frozenset(['telephone', 'home', 'office', 'no1', 'no2']),
                    }

    example_2 = nx.Graph()

    example_2.add_edge('name', 'home_address', **{EWL: 1})
    example_2.add_edge('name', 'education', **{EWL: 1})
    example_2.add_edge('education', 'bs', **{EWL: 1})
    example_2.add_edge('education', 'ms', **{EWL: 1})
    example_2.add_edge('education', 'phd', **{EWL: 1})
    example_2.add_edge('name', 'telephone', **{EWL: 1})
    example_2.add_edge('telephone', 'home', **{EWL: 1})
    example_2.add_edge('telephone', 'office', **{EWL: 1})
    example_2.add_edge('office', 'no1', **{EWL: 1})
    example_2.add_edge('office', 'no2', **{EWL: 1})

    example_2.nodes['name'][NWL] = 20
    example_2.nodes['education'][NWL] = 10
    example_2.nodes['bs'][NWL] = 1
    example_2.nodes['ms'][NWL] = 1
    example_2.nodes['phd'][NWL] = 1
    example_2.nodes['home_address'][NWL] = 8
    example_2.nodes['telephone'][NWL] = 8
    example_2.nodes['home'][NWL] = 8
    example_2.nodes['office'][NWL] = 4
    example_2.nodes['no1'][NWL] = 1
    example_2.nodes['no2'][NWL] = 1

    clusters_2 = {frozenset(x) for x in lukes_clustering(example_2, byte_block_size, node_weight=NWL, edge_weight=EWL)}

    assert clusters_2 == ground_truth


if __name__ == '__main__':
    test_paper_1()
    test_paper_2()
