import textwrap

import pytest

import networkx as nx


# Define test cases
def test_display_ascii_directed_graph():
    # Create a directed graph
    G = nx.DiGraph()
    G.add_edges_from([(1, 2), (1, 3), (2, 4)])

    # Capture the printed output
    import io
    from contextlib import redirect_stdout

    with io.StringIO() as buf, redirect_stdout(buf):
        nx.digraph_ascii(G)
        # Get the printed output
        printed_output = buf.getvalue()

    # Define expected output based on the graph structure
    expected_output = textwrap.dedent(
        """\
       └── 1
           ├── 2
           │   └── 4
           └── 3
        """
    )

    # Assert that the printed output matches the expected output
    assert printed_output == expected_output


def test_display_ascii_undirected_graph():
    # Create an undirected graph
    G = nx.Graph()
    G.add_edges_from([(1, 2), (1, 3), (2, 4)])

    # Capture the printed output
    import io
    from contextlib import redirect_stdout

    with io.StringIO() as buf, redirect_stdout(buf):
        nx.digraph_ascii(G)

        # Get the printed output
        printed_output = buf.getvalue()

    # Define expected output based on the graph structure
    expected_output = ""

    # Assert that the printed output matches the expected output
    assert printed_output == expected_output


def test_digraph_ascii_cyclic_directed_graph():
    # Create a cyclic directed graph
    G = nx.DiGraph()
    G.add_edges_from([("A", "B"), ("B", "C"), ("C", "A")])

    # Capture the printed output
    import io
    from contextlib import redirect_stdout

    with io.StringIO() as buf, redirect_stdout(buf):
        nx.digraph_ascii(G)
        # Get the printed output
        printed_output = buf.getvalue()

    # Define expected output based on the graph structure
    expected_output = "Cycles in the graph"

    # Assert that the printed output matches the expected output
    assert expected_output in printed_output
