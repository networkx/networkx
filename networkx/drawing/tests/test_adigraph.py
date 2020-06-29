import filecmp
import os

import networkx as nx


def test_basic_adigraph():
    A = nx.Adigraph(
        nodes_color_fallback="gray!90",
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
        nodes_color={
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
        nodes_color={
            0: 'green!90',
            1: 'green!90',
            4: 'purple!90',
            7: 'purple!90'
        })

    script_dir = os.path.dirname(os.path.realpath(__file__))
    testfile = "adigraph_result.tex"
    A.save(testfile, document=True)
    result = filecmp.cmp(f"{script_dir}/expected.tex", testfile)
    os.remove(testfile)
    assert result
