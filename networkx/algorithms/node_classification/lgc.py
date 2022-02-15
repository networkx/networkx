"""Function for computing Local and global consistency algorithm by Zhou et al.

References
----------
Zhou, D., Bousquet, O., Lal, T. N., Weston, J., & Schölkopf, B. (2004).
Learning with local and global consistency.
Advances in neural information processing systems, 16(16), 321-328.
"""
import networkx as nx

from networkx.utils.decorators import not_implemented_for
from networkx.algorithms.node_classification.utils import _get_label_info

__all__ = ["local_and_global_consistency"]


@not_implemented_for("directed")
def local_and_global_consistency(G, alpha=0.99, max_iter=30, label_name="label"):
    """Node classification by Local and Global Consistency

    Parameters
    ----------
    G : NetworkX Graph
    alpha : float
        Clamping factor
    max_iter : int
        Maximum number of iterations allowed
    label_name : string
        Name of target labels to predict

    Returns
    -------
    predicted : list
        List of length ``len(G)`` with the predicted labels for each node.

    Raises
    ------
    NetworkXError
        If no nodes in `G` have attribute `label_name`.

    Examples
    --------
    >>> from networkx.algorithms import node_classification
    >>> G = nx.path_graph(4)
    >>> G.nodes[0]["label"] = "A"
    >>> G.nodes[3]["label"] = "B"
    >>> G.nodes(data=True)
    NodeDataView({0: {'label': 'A'}, 1: {}, 2: {}, 3: {'label': 'B'}})
    >>> G.edges()
    EdgeView([(0, 1), (1, 2), (2, 3)])
    >>> predicted = node_classification.local_and_global_consistency(G)
    >>> predicted
    ['A', 'A', 'B', 'B']

    References
    ----------
    Zhou, D., Bousquet, O., Lal, T. N., Weston, J., & Schölkopf, B. (2004).
    Learning with local and global consistency.
    Advances in neural information processing systems, 16(16), 321-328.
    """
    import numpy as np
    import scipy as sp
    import scipy.sparse  # call as sp.sparse

    X = nx.to_scipy_sparse_array(G)  # adjacency matrix
    labels, label_dict = _get_label_info(G, label_name)

    if labels.shape[0] == 0:
        raise nx.NetworkXError(
            f"No node on the input graph is labeled by '{label_name}'."
        )

    n_samples = X.shape[0]
    n_classes = label_dict.shape[0]
    F = np.zeros((n_samples, n_classes))

    # Build propagation matrix
    degrees = X.sum(axis=0)
    degrees[degrees == 0] = 1  # Avoid division by 0
    # TODO: csr_array
    D2 = np.sqrt(sp.sparse.csr_array(sp.sparse.diags((1.0 / degrees), offsets=0)))
    P = alpha * ((D2 @ X) @ D2)
    # Build base matrix
    B = np.zeros((n_samples, n_classes))
    B[labels[:, 0], labels[:, 1]] = 1 - alpha

    for _ in range(max_iter):
        F = (P @ F) + B

    return label_dict[np.argmax(F, axis=1)].tolist()
