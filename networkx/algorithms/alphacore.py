"""AlphaCore algorithm for node ranking in directed networks."""

import math
import numbers
import warnings

import networkx as nx

__all__ = ["alpha_core"]


@nx.utils.not_implemented_for("undirected")
@nx._dispatchable
def alpha_core(G, features=None, step_size=0.1, start_epsi=1, expo_decay=False):
    """Compute the AlphaCore node ranking in a directed network.

    AlphaCore iteratively ranks nodes based on a feature set derived from
    edge attributes and node features using the Mahalanobis data depth function.

    Parameters
    ----------
    G : NetworkX graph
        A directed graph.
    features : list, optional (default=None)
        A list of selected node features. If None or ["all"], uses all
        numerical node attributes or computes default features.
    step_size : float, optional (default=0.1)
        Defines the step size of each iteration as percentage of node count.
        Higher values (>0.1) speed up execution but lower ranking resolution.
        Lower values (<0.1) provide finer ranking but increase runtime.
    start_epsi : float, optional (default=1)
        The epsilon to start with. Removes all nodes with depth>epsilon initially.
        Higher values (>1.0) remove more nodes early, emphasizing denser cores.
        Lower values (<1.0) refine ranking progressively.
    expo_decay : bool, optional (default=False)
        If True, dynamically reduces the step size to have high cores with few nodes.
        Recommended when ranking precision is more important than speed.

    Returns
    -------
    dict
        A dictionary mapping node IDs to dictionaries containing ``alpha`` and
        ``batch_id`` values.

    Notes
    -----
    AlphaCore ranks nodes when each node carries several numeric attributes
    in addition to its position in the graph.  At every outer iteration the
    algorithm removes all nodes whose Mahalanobis depth is at least the
    current threshold *epsi*.  Every node removed together is assigned the
    same alpha value, defined by

        alpha = 1 − epsi

    Larger alpha means membership in a denser, more central core.  The idea
    is analogous to the core number returned by the core_number function,
    but it is based on multivariate attributes rather than degree alone.

    Typical applications include social networks with activity or influence
    scores, financial or blockchain graphs with liquidity or risk measures,
    and infrastructure networks where nodes have capacity or reliability
    values.

    The function returns alpha values in the interval 0 to 1 (higher means
    more central) and a batch_id counter that starts at 0.

    See Also
    --------
    core_number, k_core, degree_centrality


    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_nodes_from([(0, {"f1": 0.2}), (1, {"f1": 0.7})])
    >>> G.add_edge(0, 1, value=3)
    >>> result = nx.alpha_core(G, features=["f1"])
    >>> result  # doctest: +SKIP
    {0: {'alpha': 0.2, 'batch_id': 3}, 1: {'alpha': 0.7, 'batch_id': 9}}

    References
    ----------
    .. [1] F. Victor, C.G. Akcora, Y.R. Gel, M. Kantarcioglu.
       "AlphaCore: Data Depth based Core Decomposition."
       In: Proceedings of the 27th ACM SIGKDD Conf. on Knowledge Discovery and Data Mining (KDD '21).
    """
    import numpy as np

    # Make a copy of the graph to avoid modifying the input
    graph = G.copy()

    # Handle empty graph case early
    if graph.number_of_nodes() == 0:
        return {}

    if features is None:
        features = ["all"]

    # Extract numerical node features
    data = _extract_features(graph, features)

    # Compute covariance matrix for depth calculations
    matrix = _get_feature_matrix(data)
    cov = np.cov(matrix.T)

    # Calculate initial Mahalanobis depth values
    mahal_values = _calculate_mahal_from_center(data, 0, cov, matrix)
    for node_id, mahal_val in mahal_values.items():
        data[node_id]["mahal"] = mahal_val

    epsi = start_epsi
    node = []
    alpha_vals = []
    batch = []
    alpha = 1 - epsi
    alpha_prev = alpha
    batch_id = 0

    while graph.number_of_nodes() > 0:
        while True:
            depth_found = False
            for node_id, node_data in data.items():
                if node_data["mahal"] >= epsi:
                    depth_found = True
                    node.append(node_id)
                    alpha_vals.append(alpha_prev)
                    batch.append(batch_id)
                    graph.remove_node(node_id)
            batch_id += 1

            if graph.number_of_nodes() == 0 or not depth_found:
                break

            # Recompute features and depth for remaining nodes
            data = _extract_features(graph, features)
            matrix = _get_feature_matrix(data)
            mahal_values = _calculate_mahal_from_center(data, 0, cov, matrix)
            for node_id, mahal_val in mahal_values.items():
                data[node_id]["mahal"] = mahal_val

        alpha_prev = alpha
        if expo_decay and graph.number_of_nodes() > 0:
            local_step_size = math.ceil(graph.number_of_nodes() * step_size)
            sorted_nodes = sorted(
                data.items(), key=lambda x: x[1]["mahal"], reverse=True
            )
            if local_step_size <= len(sorted_nodes):
                epsi = sorted_nodes[local_step_size - 1][1]["mahal"]
        else:
            epsi -= step_size
        alpha = 1 - epsi

    return {
        node_id: {"alpha": alpha_val, "batch_id": batch_id}
        for node_id, alpha_val, batch_id in zip(node, alpha_vals, batch)
    }


def _extract_features(graph, features=None):
    """Extract and normalize numeric node attributes for analysis.

    This function processes node attributes to create a consistent feature
    representation across all nodes. It filters for numeric attributes,
    handles missing values, and ensures all nodes have the same feature set.

    If *features* is None or equal to ["all"], every attribute that is
    numeric on at least one node is kept. When a requested attribute is
    missing or non-numeric for some nodes, its value is replaced with 0.0
    and a single warning is issued.

    Parameters
    ----------
    graph : NetworkX graph
        The directed graph to analyse.
    features : list of str or None
        Names of the attributes to keep, or None to select all numeric
        attributes.

    Returns
    -------
    dict
        Mapping node → {attribute: value}.
    """
    if graph.number_of_nodes() == 0:
        return {}

    if features is None:
        features = ["all"]
    features = list(features)

    all_numeric_keys = set()
    node_numeric_attrs = {}
    for node, attr_dict in graph.nodes(data=True):
        numeric_attrs = {
            key: value
            for key, value in attr_dict.items()
            if isinstance(value, numbers.Real) and not isinstance(value, bool)
        }
        all_numeric_keys.update(numeric_attrs.keys())
        node_numeric_attrs[node] = numeric_attrs

    selected = all_numeric_keys if features == ["all"] else set(features)
    if not selected:
        warnings.warn(
            "No numeric node attributes detected – falling back to structural features."
        )
        return _compute_default_node_features(graph)

    if features != ["all"] and not selected.issubset(all_numeric_keys):
        warnings.warn(
            "Some requested features are missing or non-numeric; "
            "missing values will be filled with 0.0."
        )

    ordered = sorted(selected)
    return {
        node: {key: node_numeric_attrs[node].get(key, 0.0) for key in ordered}
        for node in graph
    }


def _compute_default_node_features(graph, weight="weight"):
    """Return structural fallback features.

    For every node the function supplies in-degree and out-degree.
    If at least one edge carries a non-unit *weight* attribute the
    weighted strengths are added as separate columns.  When all edge
    weights equal one the strength columns are omitted so that duplicate
    information is not included.

    Parameters
    ----------
    graph : NetworkX graph
        Directed graph whose nodes are to be characterised.
    weight : str
        Edge attribute used as weight when computing strengths.

    Returns
    -------
    dict
        Mapping node → {feature: value}.
    """
    in_degree = dict(graph.in_degree())
    out_degree = dict(graph.out_degree())

    # Detect whether any edge has a non-unit weight
    has_var_weights = any(
        data.get(weight, 1) != 1 for _, _, data in graph.edges(data=True)
    )

    if has_var_weights:
        in_strength = dict(graph.in_degree(weight=weight))
        out_strength = dict(graph.out_degree(weight=weight))

    features = {}
    for node in graph:
        row = {
            "inDegree": in_degree[node],
            "outDegree": out_degree[node],
        }
        if has_var_weights:
            row["inStrength"] = in_strength[node]
            row["outStrength"] = out_strength[node]
        features[node] = row

    return features


def _get_feature_matrix(data):
    """Convert a node-feature dictionary to a float64 NumPy matrix.

    The columns appear in alphabetical order of the feature names.
    An empty input returns an empty (0 × 0) array.

    Parameters
    ----------
    data : dict
        Mapping of nodes to feature dictionaries.

    Returns
    -------
    numpy.ndarray
        Two-dimensional array with one row per node and one column per
        feature, stored as float64.
    """
    import numpy as np

    if not data:
        return np.empty((0, 0), dtype=float)

    first_node_data = next(iter(data.values()))
    feature_names = sorted(name for name in first_node_data if name != "mahal")

    if not feature_names:
        return np.empty((0, 0), dtype=float)

    matrix = []
    for node_data in data.values():
        row = [node_data[feature] for feature in feature_names]
        matrix.append(row)

    return np.asarray(matrix, dtype=float)


def _calculate_mahal_from_center(data, center, cov, matrix=None):
    """Return Mahalanobis depth for each node.

    The depth of a point is one divided by one plus its squared
    Mahalanobis distance from *center* when the covariance matrix is
    *cov*.  A pre-computed feature matrix may be supplied via *matrix*;
    if it is not given the function builds one from *data*.

    Parameters
    ----------
    data : dict
        Mapping node → feature dictionary.
    center : float or array-like
        Reference point for the distance calculation.
    cov : array-like
        Covariance matrix corresponding to the feature space.
    matrix : numpy.ndarray or None
        Optional feature matrix that matches *data*.

    Returns
    -------
    dict
        Mapping node → depth value in the range 0 to 1.
    """
    import numpy as np

    if matrix is None:
        matrix = _get_feature_matrix(data)

    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        return dict.fromkeys(data.keys(), 0.0)

    x_minus_center = matrix - center
    x_minus_center_transposed = x_minus_center.T

    # Ensure covariance matrix is at least 2D
    if np.isscalar(cov) or cov.ndim == 0:
        cov = np.array([[cov]])
    elif cov.ndim == 1:
        cov = np.array([cov]).T @ np.array([cov])

    try:
        inv_cov = np.linalg.inv(cov)
    except np.linalg.LinAlgError:
        warnings.warn(
            "Covariance matrix is not invertible, using Moore-Penrose pseudo-inverse instead."
        )
        inv_cov = np.linalg.pinv(cov)

    left = np.dot(x_minus_center, inv_cov)
    mahal = np.dot(left, x_minus_center_transposed)

    mahal_diag = np.diagonal(mahal)
    mahal_values = np.reciprocal(1 + np.maximum(mahal_diag, 0))

    node_ids = list(data.keys())
    return {
        node_id: float(depth_val) for node_id, depth_val in zip(node_ids, mahal_values)
    }
