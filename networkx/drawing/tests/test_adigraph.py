import networkx as nx
import filecmp
import random
import os
from nose.tools import assert_true

def tests_adigraph():
    seed = 7
    random.seed(seed)

    A = nx.Adigraph(
        vertices_color_fallback="gray!90",
        edges_color_fallback="gray!90",
        sub_caption="My adigraph number {i} of {n}",
        sub_label="adigraph_{i}_{n}",
        caption="A graph generated with python and latex."
    )

    G1 = nx.bipartite.random_graph(4, 4, 1, seed=42)
    layout = nx.spring_layout(G1, seed=42)

    A.add_graph(
        G1,
        layout=layout,
        vertices_color={
            0: 'red!90',
            1: 'red!90',
            4: 'cyan!90',
            7: 'cyan!90'
        }
    )
    G1 = nx.bipartite.random_graph(4, 4, 1, seed=42)
    layout = nx.spring_layout(G1, seed=42)

    A.add_graph(
        G1,
        layout=layout,
        directed=False,
        vertices_color={
            0: 'green!90',
            1: 'green!90',
            4: 'purple!90',
            7: 'purple!90'
        })

    script_dir = os.path.dirname(os.path.realpath(__file__))
    A.save("adigraph_result.tex", document=True)
    result = filecmp.cmp('{script_dir}/expected.tex'.format(script_dir=script_dir), 'adigraph_result.tex')
    os.remove("adigraph_result.tex")
    assert_true(result)