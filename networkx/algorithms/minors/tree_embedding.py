"""
Algorithm for computing the largest common tree embeddings (also known as a
minor) shared by two trees. See :func:`maximum_common_ordered_subtree_embedding`
for more details.
"""
from networkx.algorithms.string import balanced_sequence
from networkx.algorithms.string import balanced_embedding

__all__ = ["maximum_common_ordered_subtree_embedding"]


def maximum_common_ordered_subtree_embedding(
    tree1, tree2, node_affinity="auto", impl="auto", item_type="auto"
):
    r"""
    Finds the maximum common subtree-embedding between two ordered trees.

    A tree S is an embedded subtree (also known as a minor) of T if it can be
    obtained from T by a series of edge contractions.

    Subtree embeddings (or minors) are similar to tree isomorphisms --- if T is
    a subtree isomorphism then T is a minor. However, if you contract an edge in
    T it, then it may no longer be an isomorphism, but it is still a minor.

    This function computes the maximum common embedded subtrees S1 and S2
    between two trees T1 and T2. S1 and S2 are minors of T1 and T2 with maximal
    size such that S1 is isomorphic to S2.

    The computational complexity is: ``O(n1 * n2 * min(d1, l1) * min(d2, l2))``
    on ordered trees with n1 and n2 nodes, of depth d1 and d2 and with l1 and
    l2 leaves, respectively.

    This implementation follows the algorithm described in [1]_, which
    introduces the problem as follows:

    "An important generalization of tree and subtree isomorphism, known as
    minor containment, is the problem of determining whether a tree is
    isomorphic to an embedded subtree of another tree, where an embedded
    subtree of a tree is obtained by contracting some of the edges in the tree.
    A further generalization of minor containment on trees, known as maximum
    common embedded subtree, is the problem of finding or determining the size
    of a largest common embedded subtree of two trees. The latter also
    generalizes the maximum common subtree isomorphism problem, in which a
    common subtree of largest size is contained as a subtree, not only
    embedded, in the two trees."

    Parameters
    ----------
    tree1, tree2 : nx.OrderedDiGraph
        Trees to find the maximum embedding between

    node_affinity : None | str | callable
        Function for to determine if two nodes can be matched. The return is
        interpreted as a weight that is used to break ties. If None then any
        node can match any other node and only the topology is important.
        The default is "eq", which is the same as ``operator.eq``.

    impl : str
        Determines the backend implementation. Defaults to "auto".
        See :func:`networkx.algorithms.string.balanced_embedding.longest_common_balanced_embedding`
        for details. Other valid options are "iter", "recurse", and
        "iter-cython".

    item_type : str
        Determines the backend data structure used to encode the tree as a
        balanced sequence. Defaults to "auto", other valid options are "chr"
        and "number".

    Returns
    -------
    S1, S2, value: Tuple[nx.OrderedDiGraph, nx.OrderedDiGraph, float]
        The maximum value common embedding for each tree with respect to the
        chosen ``node_affinity`` function. The topology of both graphs will
        always be the same, the only difference is that the node labels in the
        first and second embeddings will correspond to ``tree1`` and ``tree2``
        respectively. When ``node_affinity='eq'`` then embeddings should be
        identical. The last return value is the "weight" of the solution with
        respect to ``node_affinity``.

    References
    ----------
    .. [1] Lozano, Antoni, and Gabriel Valiente.
        "On the maximum common embedded subtree problem for ordered trees."
        String Algorithmics (2004): 155-170.
        https://pdfs.semanticscholar.org/0b6e/061af02353f7d9b887f9a378be70be64d165.pdf

    See Also
    --------
    * For example usage see ``examples/applications/filesystem_embedding.py``
    * Core backends are in :mod:`networkx.algorithms.string.balanced_embedding.longest_common_balanced_embedding`

    Example
    -------
    >>> from networkx.algorithms.minors.tree_embedding import *  # NOQA
    >>> import networkx as nx
    >>> # Create two random trees
    >>> tree1 = nx.random_ordered_tree(7, seed=3257073545741117277206611, directed=True)
    >>> tree2 = nx.random_ordered_tree(7, seed=123568587133124688238689717, directed=True)
    >>> print(nx.forest_str(tree1))
    ╙── 0
        ├─╼ 5
        │   └─╼ 2
        └─╼ 1
            └─╼ 6
                ├─╼ 3
                └─╼ 4
    >>> print(nx.forest_str(tree2))
    ╙── 0
        └─╼ 2
            ├─╼ 1
            │   ├─╼ 4
            │   └─╼ 3
            │       └─╼ 5
            └─╼ 6
    >>> # Compute the maximum common embedding between the two trees
    >>> embedding1, embedding2, _ = maximum_common_ordered_subtree_embedding(tree1, tree2)
    >>> print(nx.forest_str(embedding1))
    ╙── 0
        └─╼ 1
            └─╼ 4
    >>> assert embedding1.edges == embedding2.edges, (
    ...     'when node_affinity is "eq" both embeddings will be the same')

    >>> # Demo with a custom node affinity where any node can match unless
    >>> # they are the same and we much prefer nodes that are disimilar
    >>> def custom_node_affinity(n1, n2):
    ...     return abs(n1 - n2) ** 2
    >>> embedding1, embedding2, _ = maximum_common_ordered_subtree_embedding(
    ...     tree1, tree2, node_affinity=custom_node_affinity)
    >>> # In this case the embeddings for each tree will be differnt
    >>> print(nx.forest_str(embedding1))
    ╙── 0
        ├─╼ 5
        │   └─╼ 2
        └─╼ 1
    >>> print(nx.forest_str(embedding2))
    ╙── 2
        ├─╼ 1
        │   └─╼ 5
        └─╼ 6
    """
    import networkx as nx

    # Note: checks that inputs are forests are handled by tree_to_seq
    if not isinstance(tree1, nx.OrderedDiGraph):
        raise nx.NetworkXNotImplemented("only implemented for directed ordered trees")
    if not isinstance(tree1, nx.OrderedDiGraph):
        raise nx.NetworkXNotImplemented("only implemented for directed ordered trees")

    if tree1.number_of_nodes() == 0 or tree2.number_of_nodes() == 0:
        raise nx.NetworkXPointlessConcept

    if item_type == "label":
        # If we do allow label, I think the algorithm will work, but the
        # returned tree embeddings will only be embedding wrt to the label
        # structure.
        raise AssertionError(
            "allowing sequences to be specified by the labels breaks assumptions"
        )

    # Convert the trees to balanced sequences.
    # NOTE: each sequence will contain each token at most once, this is an
    # important assumption in subsequent steps.
    seq1, open_to_close, node_to_open = tree_to_seq(
        tree1,
        open_to_close=None,
        node_to_open=None,
        item_type=item_type,
        container_type="auto",
    )
    seq2, open_to_close, node_to_open = tree_to_seq(
        tree2, open_to_close, node_to_open, item_type=item_type, container_type="auto"
    )

    # NOTE: This DOES work in the case where all opening tokens within a single
    # sequence are unique. And we CAN enforce that this is the case in our
    # reduction because each node in a graph is always unique and we always
    # choose a unique token for each unique node in ``tree_to_seq``.
    open_to_node = {tok: node for node, tok in node_to_open.items()}

    # Solve the longest common balanced sequence problem
    best, value = balanced_embedding.longest_common_balanced_embedding(
        seq1,
        seq2,
        open_to_close,
        open_to_node=open_to_node,
        node_affinity=node_affinity,
        impl=impl,
    )
    subseq1, subseq2 = best

    # Convert the subsequence back into a tree.
    # Note: we could return the contracted edges as well here, but that can
    # always be done as a postprocessing step. See tests for an example of
    # this.
    embedding1 = seq_to_tree(subseq1, open_to_close, open_to_node)
    embedding2 = seq_to_tree(subseq2, open_to_close, open_to_node)

    return embedding1, embedding2, value


def tree_to_seq(
    tree, open_to_close=None, node_to_open=None, item_type="auto", container_type="auto"
):
    r"""
    Converts an ordered tree to a balanced sequence --- typically with unique
    tokens --- for use in algorithm reductions.

    Used to convert a tree to a sequence before solving
    :func:`longest_common_balanced_embedding` in
    :func:`maximum_common_ordered_subtree_embedding`.

    Parameters
    ----------
    tree: nx.OrderedDiGraph
        The forest to encode as a string sequence.

    open_to_close : Dict | None
        Dictionary of opening to closing tokens to be updated for problems
        where multiple trees are converted to sequences.

    node_to_open : Dict | None
        Dictionary of nodes mapped to the opening tokens to be updated for
        problems where multiple trees are converted to sequences.

    item_type : str
        Determines the item type of the sequence.
        Can be 'auto', 'number', 'chr', or 'label'.
        Default is 'auto', which will choose 'chr' if the graph is small enough
        otherwise 'number'.  If item_type is 'label', then the label of each
        node is used to create the token, and the `open_to_close` dictionary
        must be specified.

    container_type : str
        Determines the container_type type. Can be "auto", "list", "tuple", or
        "str". If "auto" tries to choose the best given the input data.

    Returns:
    --------
    Tuple[SeqT, Dict, Dict]
        A tuple containing
            sequence - the string representation of an ordered tree
            open_to_close - a mapping between opening and closing tokens
            node_to_open - a mapping between tree nodes and opening tokens

    Examples
    --------
    >>> from networkx.algorithms.minors.tree_embedding import tree_to_seq  # NOQA
    >>> import networkx as nx
    >>> # This function helps us encode this graph as a balance sequence
    >>> tree = nx.path_graph(3, nx.OrderedDiGraph)
    >>> print(nx.forest_str(tree))
    ╙── 0
        └─╼ 1
            └─╼ 2
    >>> # The sequence is represented by opening and closing tokens
    >>> # These are returned a container, which might be a tuple of numbers
    >>> sequence, open_to_close, node_to_open, *_ = tree_to_seq(tree, item_type='number')
    >>> print(('''
    ... sequence = {sequence}
    ... open_to_close = {open_to_close}
    ... node_to_open = {node_to_open}
    ... ''').format(**locals()).strip())
    sequence = (1, 2, 3, -3, -2, -1)
    open_to_close = {1: -1, 2: -2, 3: -3}
    node_to_open = {0: 1, 1: 2, 2: 3}

    >>> # But you might also encode as a sequence of utf8-characters
    >>> # These can often be quicker to use than number encodings
    >>> sequence, open_to_close, node_to_open, *_ = tree_to_seq(tree, item_type='chr')
    >>> print(('''
    ... sequence = {sequence!r}
    ... open_to_close = {open_to_close!r}
    ... node_to_open = {node_to_open!r}
    ... ''').format(**locals()).strip())
    sequence = '\x00\x02\x04\x05\x03\x01'
    open_to_close = {'\x00': '\x01', '\x02': '\x03', '\x04': '\x05'}
    node_to_open = {0: '\x00', 1: '\x02', 2: '\x04'}

    >>> # Here is a more complex example
    >>> tree = nx.balanced_tree(2, 2, nx.DiGraph)
    >>> print(nx.forest_str(tree))
    ╙── 0
        ├─╼ 1
        │   ├─╼ 3
        │   └─╼ 4
        └─╼ 2
            ├─╼ 5
            └─╼ 6
    >>> sequence, *_ = tree_to_seq(tree, item_type='number')
    >>> print('sequence = {!r}'.format(sequence))
    sequence = (1, 2, 3, -3, 4, -4, -2, 5, 6, -6, 7, -7, -5, -1)
    >>> sequence, *_ = tree_to_seq(tree, item_type='chr')
    >>> print('sequence = {!r}'.format(sequence))
    sequence = '\x00\x02\x04\x05\x06\x07\x03\x08\n\x0b\x0c\r\t\x01'

    >>> # Demo custom label encoding: If you have custom labels on your
    >>> # tree nodes, those can be used in the encoding.
    >>> import random
    >>> tree = nx.random_ordered_tree(10, seed=1, directed=True)
    >>> rng = random.Random(0)
    >>> open_to_close = dict(zip("[{(", "]})"))
    >>> for node in tree.nodes:
    ...     tree.nodes[node]["label"] = rng.choice(list(open_to_close.keys()))
    >>> sequence, *_ = tree_to_seq(tree, item_type="label", container_type="str", open_to_close=open_to_close)
    >>> print('sequence = {!r}'.format(sequence))
    sequence = '{[{{{{}({})}{}{}}}]}'
    """
    import networkx as nx

    # Create a sequence and mapping from each index in the sequence to the
    # graph edge is corresponds to.
    sequence = []

    # mapping between opening and closing tokens
    if open_to_close is None:
        open_to_close = {}
    if node_to_open is None:
        node_to_open = {}

    # utf8 can only encode this many chars
    NUM_CHRS = 1112064
    NUM_OPEN_CHRS = NUM_CHRS // 2

    if item_type == "label":
        # Special case, where the user specifies the encoding
        all_labels = {n["label"] for n in tree.nodes.values()}

        if container_type in {"auto", "str"}:
            # Determine if the container_type can be a string
            can_be_str = all(isinstance(x, str) and len(x) == 1 for x in all_labels)
            if container_type == "str" and not can_be_str:
                raise ValueError("Labels cannot be contained as a string")
            if container_type == "auto":
                container_type = "str" if can_be_str else "tuple"

        if not open_to_close:
            raise ValueError("must specify open_to_close for custom labeling")
    else:
        # Normal case where we will define the sequence encoding for the tree
        if item_type == "auto":
            # chr mode is fastest but limited to ~half-a-million nodes
            item_type = "chr" if len(tree) < NUM_OPEN_CHRS else "number"
        if container_type == "auto":
            container_type = "str" if item_type == "chr" else "tuple"

    sources = [n for n in tree.nodes if tree.in_degree[n] == 0]
    dfs_forest_edge_gen = (
        (u, v, etype)
        for source in sources
        for u, v, etype in nx.dfs_labeled_edges(tree, source=source)
    )
    for u, v, etype in dfs_forest_edge_gen:
        if etype == "forward":
            # u has been visited by v has not
            if v not in node_to_open:
                if item_type == "number":
                    # Pos nums are open toks. Neg nums are close toks.
                    open_tok = len(node_to_open) + 1
                    close_tok = -open_tok
                elif item_type == "chr":
                    # Even chars are open toks. Odd chars are close toks.
                    open_tok = chr(len(node_to_open) * 2)
                    close_tok = chr(len(node_to_open) * 2 + 1)
                elif item_type == "label":
                    # The user must specify the closing token
                    open_tok = tree.nodes[v]["label"]
                    close_tok = open_to_close[open_tok]
                else:
                    raise KeyError(item_type)
                node_to_open[v] = open_tok
                open_to_close[open_tok] = close_tok
            open_tok = node_to_open[v]
            sequence.append(open_tok)
        elif etype == "reverse":
            # Both u and v are visited and the edge is in the tree
            close_tok = open_to_close[node_to_open[v]]
            sequence.append(close_tok)
        elif etype == "nontree":
            raise TypeError("Input must be a forest")
        else:
            raise KeyError(etype)

    if item_type == "chr":
        assert len(node_to_open) < NUM_OPEN_CHRS, "graph is way too big"

    if container_type == "str":
        sequence = "".join(sequence)
    elif container_type == "list":
        sequence = sequence
    elif container_type == "tuple":
        sequence = tuple(sequence)
    else:
        raise KeyError(container_type)

    return sequence, open_to_close, node_to_open


def seq_to_tree(subseq, open_to_close, open_to_node):
    """
    Converts a balanced sequence to an ordered tree

    Used to convert back to a tree after solving
    :func:`longest_common_balanced_embedding` in
    :func:`maximum_common_ordered_subtree_embedding`.

    Parameters
    ----------
    subseq : Tuple | str
        a balanced sequence of hashable items as a string or tuple

    open_to_close : Dict
        a dictionary that maps opening tokens to closing tokens in the balanced
        sequence problem.

    open_to_node : Dict
        a dictionary that maps a sequence token to a node corresponding to an
        original problem (e.g. a tree node). Must be unique. If unspecified new
        nodes will be generated and the opening sequence token will be used as
        a node label.

    Returns
    -------
    subtree: nx.OrderedDiGraph
        The ordered tree that corresponds to the balanced sequence

    Example
    --------
    >>> from networkx.algorithms.minors.tree_embedding import seq_to_tree
    >>> from networkx.readwrite.text import forest_str
    >>> # For a given balanced sequence
    >>> open_to_close = {'{': '}', '(': ')', '[': ']'}
    >>> open_to_node = None
    >>> subseq = '({[[]]})[[][]]{{}}'
    >>> # We can convert it into an ordered directed tree
    >>> subtree = seq_to_tree(subseq, open_to_close, open_to_node)
    >>> print(forest_str(subtree))
    ╟── (
    ╎   └─╼ {
    ╎       └─╼ [
    ╎           └─╼ [
    ╟── [
    ╎   ├─╼ [
    ╎   └─╼ [
    ╙── {
        └─╼ {
    """
    import networkx as nx

    nextnode = 0  # only used if open_to_node is not specified
    subtree = nx.OrderedDiGraph()
    stack = []
    for token in subseq:
        if token in open_to_close:
            if open_to_node is None:
                node = nextnode
                nextnode += 1
            else:
                node = open_to_node[token]
            if stack:
                parent_tok, parent_node = stack[-1]
                subtree.add_edge(parent_node, node)
            else:
                subtree.add_node(node)
            if open_to_node is None:
                subtree.nodes[node]["label"] = token
            stack.append((token, node))
        else:
            if not stack:
                raise balanced_sequence.UnbalancedException
            prev_open, prev_node = stack.pop()
            want_close = open_to_close[prev_open]
            if token != want_close:
                raise balanced_sequence.UnbalancedException
    return subtree


if __name__ == "__main__":
    """
    CommandLine:
        xdoctest -m networkx.algorithms.minors.tree_embedding all
    """
    import xdoctest

    xdoctest.doctest_module(__file__)
