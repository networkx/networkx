"""Functions for computing walks in a graph.

The simplest interface for computing the number of walks in a graph is
the :func:`number_of_walks` function. For more advanced usage, use the
:func:`single_source_number_of_walks` or
:func:`all_pairs_number_of_walks` functions.

"""
from itertools import starmap
from operator import eq

import networkx as nx

__all__ = [
    "all_pairs_number_of_walks",
    "number_of_walks",
    "single_source_number_of_walks",
]


def number_of_walks(G, walk_length, source=None, target=None):
    """Computes the number of walks of a particular length in the graph
    `G`.

    A *walk* is a sequence of nodes in which each adjacent pair of nodes
    in the sequence is adjacent in the graph.

    Neither the `source` nor the `target` nodes are required for this
    function; see the *Returns* section for more information on how
    these keyword arguments affect the output of this function.

    Parameters
    ----------
    G : NetworkX graph
        The node labels for a graph on *n* nodes
        must be the integers {0, …, *n* - 1}. If not, a :exc:`TypeError`
        or :exc:`ValueError` is raised.

    walk_length: int
        A nonnegative integer representing the length of a walk.

    source : node
        A node in the graph `G`. If not specified, the number of walks
        from all possible source nodes in the graph will be computed.

    target : node
        A node in the graph `G`. If not specified, the number of walks
        to all possible target nodes in the graph will be computed.

    Returns
    -------
    dict or int
        If both `source` and `target` are specified, the number of walks
        connecting `source` to `target` of length `walk_length` is
        returned.

        If `source` but not `target` is specified, the return value is a
        dictionary whose keys are target nodes and whose values are the
        number of walks of length `walk_length` from the source node to
        the target node.

        If `target` but not `source` is specified, the return value is a
        dictionary whose keys are source nodes and whose values are the
        number of walks of length `walk_length` from the source node to
        the target node.

        If neither `source` nor `target` are specified, this returns a
        dictionary of dictionaries in which outer keys are source nodes,
        inner keys are target nodes, and inner values are the number of
        walks of length `walk_length` connecting those nodes.

    Raises
    ------
    ValueError
        If `walk_length` is negative,  or if the node labels
        of the graph are integers but not the integers between 0 and *n*
        - 1, inclusive.

    TypeError
        If the node labels of the graph are not
        integers.

    """
    if source is None and target is None:
        return all_pairs_number_of_walks(G, walk_length)
    # Rename this function for the sake of brevity.
    single_source = single_source_number_of_walks
    if source is None and target is not None:
        # Temporarily reverse the edges of the graph *in-place*, then
        # compute the number of walks from target to the various
        # sources.
        G = G.reverse(copy=False)
        return single_source(G, walk_length, target)
    return single_source(G, walk_length, source, target=target)


def single_source_number_of_walks(G, walk_length, source, target=None):
    """Returns the number of walks from `source` to each other node in
    the graph `G`.

    A *walk* is a sequence of nodes in which each adjacent pair of nodes
    in the sequence is adjacent in the graph.

    Parameters
    ----------
    G : NetworkX graph
        The node labels for a graph on *n* nodes
        must be the integers {0, …, *n* - 1}. If not, a :exc:`TypeError`
        or :exc:`ValueError` is raised.

    walk_length: int
        A nonnegative integer representing the length of a walk.

    source : node
        A node in the graph `G`.

    target : node
        A node in the graph `G`. If not specified, the number of walks
        from `source` to each other node in the graph is returned.

    Returns
    -------
    dict or int
        If `target` is not specified, the return value is a dictionary
        whose keys are target nodes and whose values are the number of
        walks of length `walk_length` from the source node to the target
        node.

        If `target` is a node in the graph, this simply returns the
        number of walks from `source` to `target` in `G`.

    Raises
    ------
    ValueError
        If `walk_length` is negative, or if the node labels
        of the graph are integers but not the integers between 0 and *n*
        - 1, inclusive.

    TypeError
        If the node labels of the graph are not
        integers.

    """
    A = nx.adjacency_matrix(G, nodelist=list(G))
    power = A**walk_length
    if target is not None:
        return power[source, target]
    entries = _matrix_entries(power, row=source)
    result = {v: 0 for v in G}
    for v, d in entries:
        result[v] = d
    return result


def all_pairs_number_of_walks(G, walk_length):
    """Returns the number of walks connecting each pair of nodes in
    `G`.

    A *walk* is a sequence of nodes in which each adjacent pair of nodes
    in the sequence is adjacent in the graph.

    Parameters
    ----------
    G : NetworkX graph
        The node labels for a graph on *n* nodes
        must be the integers {0, …, *n* - 1}. If not, a :exc:`TypeError`
        or :exc:`ValueError` is raised.

    walk_length : int
        A nonnegative integer representing the length of a walk.

    Returns
    -------
    dict
        A dictionary of dictionaries in which outer keys are source
        nodes, inner keys are target nodes, and inner values are the
        number of walks of length `walk_length` connecting those nodes.

    Raises
    ------
    ValueError
        If `walk_length` is negative, or if  the node labels
        of the graph are integers but not the integers between 0 and *n*
        - 1, inclusive.

    TypeError
        If the node labels of the graph are not
        integers.

    """
    A = nx.adjacency_matrix(G)
    power = A**walk_length
    result = {u: {v: 0 for v in G} for u in G}
    # `u` is the source node, `v` is the target node, and `d` is the
    # number of walks with initial node `u` and terminal node `v`.
    for u, v, d in _matrix_entries(power):
        result[u][v] = d
    return result


def _csr_matrix_entries(A, row=None):
    """Iterator over the nonzero entries of the matrix `A`.
    `A` is a SciPy sparse matrix in Compressed Sparse Row ('csr')
    format.
    If `row` is specified, this function iterates over pairs of the form
    ``(j, A[row, j])``. Otherwise, this function iterates over triples
    of the form ``(i, j, A[i, j])``.
    """
    data, indices, indptr = A.data, A.indices, A.indptr
    if row is None:
        nrows = A.shape[0]
        for i in range(nrows):
            for j in range(indptr[i], indptr[i + 1]):
                yield i, indices[j], data[j]
    else:
        i = row
        for j in range(indptr[i], indptr[i + 1]):
            yield indices[j], data[j]


def _csc_matrix_entries(A, row=None):
    """Iterator over the nonzero entries of the matrix `A`.
    `A` is a SciPy sparse matrix in Compressed Sparse Column ('csc')
    format.
    If `row` is specified, this function iterates over pairs of the form
    ``(j, A[row, j])``. Otherwise, this function iterates over triples
    of the form ``(i, j, A[i, j])``.
    """
    ncols = A.shape[1]
    if row is None:
        data, indices, indptr = A.data, A.indices, A.indptr
        for i in range(ncols):
            for j in range(indptr[i], indptr[i + 1]):
                yield indices[j], i, data[j]
    else:
        # Calling the `getrow()` method on a 'csc' sparse matrix returns
        # a 'csr' sparse matrix representing just that row.
        for i, j, x in _csr_matrix_entries(A.getrow(row)):
            yield j, x


def _coo_matrix_entries(A, row=None):
    """Iterator over the nonzero entries of the matrix `A`.
    `A` is a SciPy sparse matrix in COOrdinate ('coo') format.
    If `row` is specified, this function iterates over pairs of the form
    ``(j, A[row, j])``. Otherwise, this function iterates over triples
    of the form ``(i, j, A[i, j])``.
    """
    if row is None:
        row, col, data = A.row, A.col, A.data
        # TODO In Python 3.3+, this should be `yield from ...`.
        for i, j, x in zip(row, col, data):
            yield i, j, x
    else:
        # Calling the `getrow()` method on a 'coo' sparse matrix returns
        # a 'csr' sparse matrix representing just that row.
        for i, j, x in _csr_matrix_entries(A.getrow(row)):
            yield j, x


def _dok_matrix_entries(A, row=None):
    """Iterator over the nonzero entries of the matrix `A`.
    `A` is a SciPy sparse matrix in Dictionary Of Keys ('dok') format.
    If `row` is specified, this function iterates over pairs of the form
    ``(j, A[row, j])``. Otherwise, this function iterates over triples
    of the form ``(i, j, A[i, j])``.
    """
    if row is None:
        for (r, c), v in A.items():
            yield r, c, v
    else:
        # We are guaranteed that each `r` equals `row`.
        for (r, c), v in A[row].items():
            yield c, v


def _matrix_entries(A, row=None):
    """Iterator over the nonzero entries of the matrix `A`.
    `A` is a SciPy sparse matrix in any format.
    If `row` is specified, this function iterates over pairs of the form
    ``(j, A[row, j])``. Otherwise, this function iterates over triples
    of the form ``(i, j, A[i, j])``.
    """
    if A.format == "csr":
        return _csr_matrix_entries(A, row=row)
    if A.format == "csc":
        return _csc_matrix_entries(A, row=row)
    if A.format == "dok":
        return _dok_matrix_entries(A, row=row)
    # If A is in any other format (including COO), convert it to COO format.
    return _coo_matrix_entries(A.tocoo(), row=row)
