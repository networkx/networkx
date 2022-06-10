import filecmp
import os

import networkx as nx
import pytest


def test_multiple_graphs():
    H1 = nx.path_graph(4)
    H2 = nx.complete_graph(4)
    H3 = nx.path_graph(8)
    H4 = nx.complete_graph(8)
    captions = [
        "Path on 4 nodes",
        "Complete graph on 4 nodes",
        "Path on 8 nodes",
        "Complete graph on 8 nodes",
    ]
    labels = ["fig2a", "fig2b", "fig2c", "fig2d"]
    latex_code = nx.to_latex(
        [H1, H2, H3, H4],
        n_rows=2,
        sub_captions=captions,
        sub_labels=labels,
    )


expected_tex = r"""\documentclass{report}
\usepackage{adigraph}
\usepackage{subcaption}

\begin{document}
\begin{figure}
    \begin{subfigure}{0.5\textwidth}
        \NewAdigraph{myAdigraph}{
            0,red!90,:0.3745148085843848\textwidth,0.351176760128697\textwidth:;
            1,red!90,:0.5\textwidth,-0.007110678861898268\textwidth:;
            2,gray!90,:-0.38828916720807205\textwidth,-0.35270854834044596\textwidth:;
            3,gray!90,:-0.4921345111708812\textwidth,0.020887738012327416\textwidth:;
            4,cyan!90,:-0.013842619085904584\textwidth,0.18728622197757205\textwidth:;
            5,gray!90,:-0.20577427573383716\textwidth,0.4440053257762568\textwidth:;
            6,gray!90,:0.22390076694574132\textwidth,-0.4280746354634582\textwidth:;
            7,cyan!90,:0.0016249976685691753\textwidth,-0.21546218322904973\textwidth:;
        }{
            0,4,gray!90,::;
            0,5,gray!90,::;
            0,6,gray!90,::;
            0,7,gray!90,::;
            1,4,gray!90,::;
            1,5,gray!90,::;
            1,6,gray!90,::;
            1,7,gray!90,::;
            2,4,gray!90,::;
            2,5,gray!90,::;
            2,6,gray!90,::;
            2,7,gray!90,::;
            3,4,gray!90,::;
            3,5,gray!90,::;
            3,6,gray!90,::;
            3,7,gray!90,::;
        }[]
        \myAdigraph{}
    \caption{My adigraph number 1 of 2}\label{adigraph_1_2}
    \end{subfigure}
    \begin{subfigure}{0.5\textwidth}
        \NewAdigraph{myAdigraph}{
            0,green!90,:0.3745148085843848\textwidth,0.351176760128697\textwidth:;
            1,green!90,:0.5\textwidth,-0.007110678861898268\textwidth:;
            2,gray!90,:-0.38828916720807205\textwidth,-0.35270854834044596\textwidth:;
            3,gray!90,:-0.4921345111708812\textwidth,0.020887738012327416\textwidth:;
            4,purple!90,:-0.013842619085904584\textwidth,0.18728622197757205\textwidth:;
            5,gray!90,:-0.20577427573383716\textwidth,0.4440053257762568\textwidth:;
            6,gray!90,:0.22390076694574132\textwidth,-0.4280746354634582\textwidth:;
            7,purple!90,:0.0016249976685691753\textwidth,-0.21546218322904973\textwidth:;
        }{
            0,4,gray!90,::;
            0,5,gray!90,::;
            0,6,gray!90,::;
            0,7,gray!90,::;
            1,4,gray!90,::;
            1,5,gray!90,::;
            1,6,gray!90,::;
            1,7,gray!90,::;
            2,4,gray!90,::;
            2,5,gray!90,::;
            2,6,gray!90,::;
            2,7,gray!90,::;
            3,4,gray!90,::;
            3,5,gray!90,::;
            3,6,gray!90,::;
            3,7,gray!90,::;
        }[]
        \myAdigraph{}
    \caption{My adigraph number 2 of 2}\label{adigraph_2_2}
    \end{subfigure}
    \caption{A graph generated with python and latex.}
\end{figure}
\end{document}
"""


def test_basic_adigraph():
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
    G = nx.DiGraph()
    G.add_nodes_from(range(8))
    G.add_edges_from(edges)
    pos = {
        0: (0.7490296171687696, 0.702353520257394),
        1: (1.0, -0.014221357723796535),
        2: (-0.7765783344161441, -0.7054170966808919),
        3: (-0.9842690223417624, 0.04177547602465483),
        4: (-0.02768523817180917, 0.3745724439551441),
        5: (-0.41154855146767433, 0.8880106515525136),
        6: (0.44780153389148264, -0.8561492709269164),
        7: (0.0032499953371383505, -0.43092436645809945),
    }

    rc_node_color = {0: "red!90", 1: "red!90", 4: "cyan!90", 7: "cyan!90"}
    gp_node_color = {0: "green!90", 1: "green!90", 4: "purple!90", 7: "purple!90"}

    H = G.copy()
    nx.set_node_attributes(G, rc_node_color, "color")
    nx.set_node_attributes(H, gp_node_color, "color")

    sub_captions = ["My adigraph number 1 of 2", "My adigraph number 2 of 2"]
    sub_labels = ["adigraph_1_2", "adigraph_2_2"]

    output_tex = nx.to_latex(
        [G, H],
        [pos, pos],
        default_node_color="gray!90",
        default_edge_color="gray!90",
        sub_captions=sub_captions,
        sub_labels=sub_labels,
        caption="A graph generated with python and latex.",
        n_rows=2,
        as_document=True,
    )

    # Pretty way to assert that A.to_document() == expected_tex
    content_same = True
    for aa, bb in zip(expected_tex.split("\n"), output_tex.split("\n")):
        if aa != bb:
            content_same = False
            print(f"-{aa}|\n+{bb}|")
    assert content_same


def test_exception_pos_single_graph():
    G = nx.path_graph(4)
    with pytest.raises(nx.NetworkXError):
        nx.to_latex(G, pos="pos")

    pos = {0: (1, 2), 1: (0, 1), 2: (2, 1)}
    with pytest.raises(nx.NetworkXError):
        nx.to_latex(G, pos)

    pos[3] = (1, 2, 3)
    with pytest.raises(nx.NetworkXError):
        nx.to_latex(G, pos)

    pos[3] = (3, 2)
    nx.to_latex(G, pos)


def test_exception_multiple_graphs():
    G = nx.path_graph(3)
    pos_bad = {0: (1, 2), 1: (0, 1)}
    pos_OK = {0: (1, 2), 1: (0, 1), 2: (2, 1)}
    fourG = [G, G, G, G]
    fourpos = [pos_OK, pos_OK, pos_OK, pos_OK]

    with pytest.raises(nx.NetworkXError):
        nx.to_latex(fourG, pos_OK)

    with pytest.raises(nx.NetworkXError):
        nx.to_latex(fourG, pos_bad)

    with pytest.raises(nx.NetworkXError):
        nx.to_latex(fourG, [pos_bad, pos_bad, pos_bad, pos_bad])

    with pytest.raises(nx.NetworkXError):
        nx.to_latex(fourG, [pos_OK, pos_OK, pos_bad, pos_OK])

    nx.to_latex(fourG, fourpos)

    # test sub_captions and sub_labels
    with pytest.raises(nx.NetworkXError):
        nx.to_latex(fourG, fourpos, sub_captions=["hi", "hi"])

    with pytest.raises(nx.NetworkXError):
        nx.to_latex(fourG, fourpos, sub_labels=["hi", "hi"])

    nx.to_latex(fourG, fourpos, ["hi"] * 4, ["lbl"] * 4)


def test_exception_multigraph():
    G = nx.MultiGraph()
    with pytest.raises(nx.NetworkXNotImplemented):
        nx.to_latex(G)
