import filecmp
import os

import networkx as nx


def test_basic_adigraph():
    A = nx.Adigraph(
        nodes_color_fallback="gray!90",
        edges_color_fallback="gray!90",
        sub_caption="My adigraph number {i} of {n}",
        sub_label="adigraph_{i}_{n}",
        caption="A graph generated with python and latex.",
    )

    edges = [
        (0, 4),
        (0, 5),
        (0, 6),
        (0, 7),
        (1, 4),
        (1, 5),
        (1, 6),
        (1, 7),
        (2, 4),
        (2, 5),
        (2, 6),
        (2, 7),
        (3, 4),
        (3, 5),
        (3, 6),
        (3, 7),
    ]
    G = nx.Graph()
    G.add_nodes_from(range(8))
    G.add_edges_from(edges)
    layout = {
        0: (0.7490296171687696, 0.702353520257394),
        1: (1.0, -0.014221357723796535),
        2: (-0.7765783344161441, -0.7054170966808919),
        3: (-0.9842690223417624, 0.04177547602465483),
        4: (-0.02768523817180917, 0.3745724439551441),
        5: (-0.41154855146767433, 0.8880106515525136),
        6: (0.44780153389148264, -0.8561492709269164),
        7: (0.0032499953371383505, -0.43092436645809945),
    }

    A.add_graph(
        G,
        layout=layout,
        nodes_color={0: "red!90", 1: "red!90", 4: "cyan!90", 7: "cyan!90"},
    )

    A.add_graph(
        G,
        layout=layout,
        directed=False,
        nodes_color={0: "green!90", 1: "green!90", 4: "purple!90", 7: "purple!90"},
    )

    script_dir = os.path.dirname(os.path.realpath(__file__))
    testfile = "adigraph_result.tex"
    A.save(testfile, document=True)
    result = filecmp.cmp(f"{script_dir}/expected.tex", testfile)
    with open(testfile, "r") as f:
        fileresult = f.readlines()
    os.remove(testfile)

    expected_filename = f"{script_dir}/expected.tex"
    with open(expected_filename, "r") as f:
        expected = f.readlines()

    content_same = True
    for aa, bb in zip(expected, fileresult):
        if aa != bb:
            content_same = False
            print(aa, "|||", bb, "|end|")
    assert content_same
