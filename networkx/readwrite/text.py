"""
Text-based visual representations of graphs
"""
import sys
import warnings
from collections import defaultdict

import networkx as nx
from networkx.utils import open_file

__all__ = ["forest_str", "generate_network_text", "write_network_text"]


class _AsciiBaseGlyphs:
    empty = "+"
    newtree_last = "+-- "
    newtree_mid = "+-- "
    endof_forest = "    "
    within_forest = ":   "
    within_tree = "|   "


class AsciiDirectedGlyphs(_AsciiBaseGlyphs):
    last = "L-> "
    mid = "|-> "
    backedge = "<-"


class AsciiUndirectedGlyphs(_AsciiBaseGlyphs):
    last = "L-- "
    mid = "|-- "
    backedge = "-"


class _UtfBaseGlyphs:
    # Notes on available box and arrow characters
    # https://en.wikipedia.org/wiki/Box-drawing_character
    # https://stackoverflow.com/questions/2701192/triangle-arrow
    empty = "╙"
    newtree_last = "╙── "
    newtree_mid = "╟── "
    endof_forest = "    "
    within_forest = "╎   "
    within_tree = "│   "


class UtfDirectedGlyphs(_UtfBaseGlyphs):
    last = "└─╼ "
    mid = "├─╼ "
    backedge = "╾"


class UtfUndirectedGlyphs(_UtfBaseGlyphs):
    last = "└── "
    mid = "├── "
    backedge = "─"


def generate_network_text(
    graph, with_labels=True, sources=None, max_depth=None, ascii_only=False
):
    """Generate lines in the "network text" format

    This works via a depth-first traversal of the graph and writing a line for
    each unique node encountered. Non-tree edges are written to the right of
    each node, and connection to a non-tree edge is indicated with an ellipsis.
    This representation works best when the input graph is a forest, but any
    graph can be represented.

    This notation is original to networkx, although it is simple enough that it
    may be known in existing literature. See #5602 for details. The procedure
    is summarized as follows:

    1. Given a set of source nodes (which can be specified, or automatically
    discovered via finding the (strongly) connected components and choosing one
    node with minimum degree from each), we traverse the graph in depth first
    order.

    2. Each reachable node will be printed exactly once on it's own line.

    3. Edges are indicated in one of three ways:

        a. a parent "L-style" connection on the upper left. This corresponds to
        a traversal in the directed DFS tree.

        b. a backref "<-style" connection shown directly on the right. For
        directed graphs, these are drawn for any incoming edges to a node that
        is not a parent edge. For undirected graphs, these are drawn for only
        the non-parent edges that have already been represented (The edges that
        have not been represented will be handled in the recursive case).

        c. a child "L-style" connection on the lower right. Drawing of the
        children are handled recursively.

    4. The children of each node (wrt the directed DFS tree) are drawn
    underneath and to the right of it. In the case that a child node has already
    been drawn the connection is replaced with an ellipsis ("...") to indicate
    that there is one or more connections represented elsewhere.

    5. If a maximum depth is specified, an edge to nodes past this maximum
    depth will be represented by an ellipsis.

    Parameters
    ----------
    graph : nx.DiGraph | nx.Graph
        Graph to represent

    with_labels : bool | str
        If True will use the "label" attribute of a node to display if it
        exists otherwise it will use the node value itself. If given as a
        string, then that attribute name will be used instead of "label".
        Defaults to True.

    sources : List
        Specifies which nodes to start traversal from. Note: nodes that are not
        reachable from one of these sources may not be shown. If unspecified,
        the minimal set of nodes needed to reach all others will be used.

    max_depth : int | None
        The maximum depth to traverse before stopping. Defaults to None.

    ascii_only : Boolean
        If True only ASCII characters are used to construct the visualization

    Yields
    ------
    str : a line of generated text
    """
    is_directed = graph.is_directed()

    if is_directed:
        glyphs = AsciiDirectedGlyphs if ascii_only else UtfDirectedGlyphs
        succ = graph.succ
        pred = graph.pred
    else:
        glyphs = AsciiUndirectedGlyphs if ascii_only else UtfUndirectedGlyphs
        succ = graph.adj
        pred = graph.adj

    if isinstance(with_labels, str):
        label_attr = with_labels
    elif with_labels:
        label_attr = "label"
    else:
        label_attr = None

    if max_depth == 0:
        yield glyphs.empty + " ..."
    elif len(graph.nodes) == 0:
        yield glyphs.empty
    else:
        # If the nodes to traverse are unspecified, find the minimal set of
        # nodes that will reach the entire graph
        if sources is None:
            sources = _find_sources(graph)

        # Populate the stack with each:
        # 1. parent node in the DFS tree (or None for root nodes),
        # 2. the current node in the DFS tree
        # 2. a list of indentations indicating depth
        # 3. a flag indicating if the node is the final one to be written.
        # Reverse the stack so sources are popped in the correct order.
        last_idx = len(sources) - 1
        stack = [
            (None, node, [], (idx == last_idx)) for idx, node in enumerate(sources)
        ][::-1]

        num_skipped_children = defaultdict(lambda: 0)
        seen_nodes = set()
        while stack:
            parent, node, indents, this_islast = stack.pop()

            if node is not Ellipsis:
                skip = node in seen_nodes
                if skip:
                    # Mark that we skipped a parent's child
                    num_skipped_children[parent] += 1

                if this_islast:
                    # If we reached the last child of a parent, and we skipped
                    # any of that parents children, then we should emit an
                    # ellipsis at the end after this.
                    if num_skipped_children[parent] and parent is not None:
                        # Append the ellipsis to be emitted last
                        next_islast = True
                        try_frame = (node, Ellipsis, indents, next_islast)
                        stack.append(try_frame)

                        # Redo this frame, but not as a last object
                        next_islast = False
                        try_frame = (parent, node, indents, next_islast)
                        stack.append(try_frame)
                        continue

                if skip:
                    continue
                seen_nodes.add(node)

            if not indents:
                # Top level items (i.e. trees in the forest) get different
                # glyphs to indicate they are not actually connected
                if this_islast:
                    this_prefix = indents + [glyphs.newtree_last]
                    next_prefix = indents + [glyphs.endof_forest]
                else:
                    this_prefix = indents + [glyphs.newtree_mid]
                    next_prefix = indents + [glyphs.within_forest]

            else:
                # For individual tree edges distinguish between directed and
                # undirected cases
                if this_islast:
                    this_prefix = indents + [glyphs.last]
                    next_prefix = indents + [glyphs.endof_forest]
                else:
                    this_prefix = indents + [glyphs.mid]
                    next_prefix = indents + [glyphs.within_tree]

            if node is Ellipsis:
                label = " ..."
                suffix = ""
                children = []
            else:
                if label_attr is not None:
                    label = str(graph.nodes[node].get(label_attr, node))
                else:
                    label = str(node)

                # Determine:
                # (1) children to traverse into after showing this node.
                # (2) parents to immediately show to the right of this node.
                if is_directed:
                    # In the directed case we must show every successor node
                    # note: it may be skipped later, but we don't have that
                    # information here.
                    children = list(succ[node])
                    # In the directed case we must show every predecessor
                    # except for parent we directly traversed from.
                    handled_parents = {parent}
                else:
                    # Showing only the unseen children results in a more
                    # concise representation for the undirected case.
                    children = [
                        child for child in succ[node] if child not in seen_nodes
                    ]

                    # In the undirected case, parents are also children, so we
                    # only need to immediately show the ones we can no longer
                    # traverse
                    handled_parents = {*children, parent}

                if max_depth is not None and len(indents) == max_depth - 1:
                    # Use ellipsis to indicate we have reached maximum depth
                    if children:
                        children = [Ellipsis]
                    handled_parents = {parent}

                # The other parents are other predecessors of this node that
                # are not handled elsewhere.
                other_parents = [p for p in pred[node] if p not in handled_parents]
                if other_parents:
                    if label_attr is not None:
                        other_parents_labels = ", ".join(
                            [
                                str(graph.nodes[p].get(label_attr, p))
                                for p in other_parents
                            ]
                        )
                    else:
                        other_parents_labels = ", ".join(
                            [str(p) for p in other_parents]
                        )
                    suffix = " ".join(["", glyphs.backedge, other_parents_labels])
                else:
                    suffix = ""

            # Emit the line for this node, this will be called for each node
            # exactly once.
            yield "".join(this_prefix + [label, suffix])

            # Push children on the stack in reverse order so they are popped in
            # the original order.
            for idx, child in enumerate(children[::-1]):
                next_islast = idx == 0
                try_frame = (node, child, next_prefix, next_islast)
                stack.append(try_frame)


@open_file(1, "w")
def write_network_text(
    graph,
    path=None,
    with_labels=True,
    sources=None,
    max_depth=None,
    ascii_only=False,
    end="\n",
):
    """Creates a nice text representation of a graph

    This works via a depth-first traversal of the graph and writing a line for
    each unique node encountered. Non-tree edges are written to the right of
    each node, and connection to a non-tree edge is indicated with an ellipsis.
    This representation works best when the input graph is a forest, but any
    graph can be represented.

    Parameters
    ----------
    graph : nx.DiGraph | nx.Graph
        Graph to represent

    path : string or file or callable or None
       Filename or file handle for data output.
       if a function, then it will be called for each generated line.
       if None, this will default to "sys.stdout.write"

    with_labels : bool | str
        If True will use the "label" attribute of a node to display if it
        exists otherwise it will use the node value itself. If given as a
        string, then that attribute name will be used instead of "label".
        Defaults to True.

    sources : List
        Specifies which nodes to start traversal from. Note: nodes that are not
        reachable from one of these sources may not be shown. If unspecified,
        the minimal set of nodes needed to reach all others will be used.

    max_depth : int | None
        The maximum depth to traverse before stopping. Defaults to None.

    ascii_only : Boolean
        If True only ASCII characters are used to construct the visualization

    end : string
        The line ending character

    Examples
    --------
    >>> graph = nx.balanced_tree(r=2, h=2, create_using=nx.DiGraph)
    >>> nx.write_network_text(graph)
    ╙── 0
        ├─╼ 1
        │   ├─╼ 3
        │   └─╼ 4
        └─╼ 2
            ├─╼ 5
            └─╼ 6

    >>> # A near tree with one non-tree edge
    >>> graph.add_edge(5, 1)
    >>> nx.write_network_text(graph)
    ╙── 0
        ├─╼ 1 ╾ 5
        │   ├─╼ 3
        │   └─╼ 4
        └─╼ 2
            ├─╼ 5
            │   └─╼  ...
            └─╼ 6

    >>> graph = nx.cycle_graph(5)
    >>> nx.write_network_text(graph)
    ╙── 0
        ├── 1
        │   └── 2
        │       └── 3
        │           └── 4 ─ 0
        └──  ...

    >>> graph = nx.generators.barbell_graph(4, 2)
    >>> nx.write_network_text(graph)
    ╙── 4
        ├── 5
        │   └── 6
        │       ├── 7
        │       │   ├── 8 ─ 6
        │       │   │   └── 9 ─ 6, 7
        │       │   └──  ...
        │       └──  ...
        └── 3
            ├── 0
            │   ├── 1 ─ 3
            │   │   └── 2 ─ 0, 3
            │   └──  ...
            └──  ...

    >>> graph = nx.complete_graph(5, create_using=nx.Graph)
    >>> nx.write_network_text(graph)
    ╙── 0
        ├── 1
        │   ├── 2 ─ 0
        │   │   ├── 3 ─ 0, 1
        │   │   │   └── 4 ─ 0, 1, 2
        │   │   └──  ...
        │   └──  ...
        └──  ...

    >>> graph = nx.complete_graph(3, create_using=nx.DiGraph)
    >>> nx.write_network_text(graph)
    ╙── 0 ╾ 1, 2
        ├─╼ 1 ╾ 2
        │   ├─╼ 2 ╾ 0
        │   │   └─╼  ...
        │   └─╼  ...
        └─╼  ...
    """
    if path is None:
        # The path is unspecified, write to stdout
        _write = sys.stdout.write
    elif hasattr(path, "write"):
        # The path is already an open file
        _write = path.write
    elif callable(path):
        # The path is a custom callable
        _write = path
    else:
        raise TypeError(type(path))

    for line in generate_network_text(
        graph,
        with_labels=with_labels,
        sources=sources,
        max_depth=max_depth,
        ascii_only=ascii_only,
    ):
        _write(line + end)


def _find_sources(graph):
    """
    Determine a minimal set of nodes such that the entire graph is reachable
    """
    # For each connected part of the graph, choose at least
    # one node as a starting point, preferably without a parent
    if graph.is_directed():
        # Choose one node from each SCC with minimum in_degree
        sccs = list(nx.strongly_connected_components(graph))
        # condensing the SCCs forms a dag, the nodes in this graph with
        # 0 in-degree correspond to the SCCs from which the minimum set
        # of nodes from which all other nodes can be reached.
        scc_graph = nx.condensation(graph, sccs)
        supernode_to_nodes = {sn: [] for sn in scc_graph.nodes()}
        # Note: the order of mapping differs between pypy and cpython
        # so we have to loop over graph nodes for consistency
        mapping = scc_graph.graph["mapping"]
        for n in graph.nodes:
            sn = mapping[n]
            supernode_to_nodes[sn].append(n)
        sources = []
        for sn in scc_graph.nodes():
            if scc_graph.in_degree[sn] == 0:
                scc = supernode_to_nodes[sn]
                node = min(scc, key=lambda n: graph.in_degree[n])
                sources.append(node)
    else:
        # For undirected graph, the entire graph will be reachable as
        # long as we consider one node from every connected component
        sources = [
            min(cc, key=lambda n: graph.degree[n])
            for cc in nx.connected_components(graph)
        ]
        sources = sorted(sources, key=lambda n: graph.degree[n])
    return sources


def forest_str(graph, with_labels=True, sources=None, write=None, ascii_only=False):
    """Creates a nice utf8 representation of a forest

    This function has been superseded by
    :func:`nx.readwrite.text.generate_network_text`, which should be used
    instead.

    Parameters
    ----------
    graph : nx.DiGraph | nx.Graph
        Graph to represent (must be a tree, forest, or the empty graph)

    with_labels : bool
        If True will use the "label" attribute of a node to display if it
        exists otherwise it will use the node value itself. Defaults to True.

    sources : List
        Mainly relevant for undirected forests, specifies which nodes to list
        first. If unspecified the root nodes of each tree will be used for
        directed forests; for undirected forests this defaults to the nodes
        with the smallest degree.

    write : callable
        Function to use to write to, if None new lines are appended to
        a list and returned. If set to the `print` function, lines will
        be written to stdout as they are generated. If specified,
        this function will return None. Defaults to None.

    ascii_only : Boolean
        If True only ASCII characters are used to construct the visualization

    Returns
    -------
    str | None :
        utf8 representation of the tree / forest

    Examples
    --------
    >>> graph = nx.balanced_tree(r=2, h=3, create_using=nx.DiGraph)
    >>> print(nx.forest_str(graph))
    ╙── 0
        ├─╼ 1
        │   ├─╼ 3
        │   │   ├─╼ 7
        │   │   └─╼ 8
        │   └─╼ 4
        │       ├─╼ 9
        │       └─╼ 10
        └─╼ 2
            ├─╼ 5
            │   ├─╼ 11
            │   └─╼ 12
            └─╼ 6
                ├─╼ 13
                └─╼ 14


    >>> graph = nx.balanced_tree(r=1, h=2, create_using=nx.Graph)
    >>> print(nx.forest_str(graph))
    ╙── 0
        └── 1
            └── 2

    >>> print(nx.forest_str(graph, ascii_only=True))
    +-- 0
        L-- 1
            L-- 2
    """
    msg = (
        "\nforest_str is deprecated as of version 3.1 and will be removed "
        "in version 3.3. Use generate_network_text or write_network_text "
        "instead.\n"
    )
    warnings.warn(msg, DeprecationWarning)

    if len(graph.nodes) > 0:
        if not nx.is_forest(graph):
            raise nx.NetworkXNotImplemented("input must be a forest or the empty graph")

    printbuf = []
    if write is None:
        _write = printbuf.append
    else:
        _write = write

    write_network_text(
        graph,
        _write,
        with_labels=with_labels,
        sources=sources,
        ascii_only=ascii_only,
        end="",
    )

    if write is None:
        # Only return a string if the custom write function was not specified
        return "\n".join(printbuf)
