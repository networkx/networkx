"""AlphaCore algorithm for node ranking in a directed network.

The algorithm iteratively computes a node ranking based on a feature set
using the Mahalanobis data depth function at the origin.
"""

import math
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
        A dictionary mapping node IDs to dictionaries containing 'alpha' and 'batchID' values.

    Notes
    -----
    The function references numbered steps (#1, #2, etc.) to align with
    the AlphaCore article's algorithmic outline.

    References
    ----------
    .. [1] F. Victor, C.G. Akcora, Y.R. Gel, M. Kantarcioglu.
       "AlphaCore: Data Depth based Core Decomposition."
       In: Proceedings of the 27th ACM SIGKDD Conf. on Knowledge Discovery and Data Mining (KDD '21).

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> G.add_nodes_from(
    ...     [
    ...         (0, {"f1": 0.2}),
    ...         (1, {"f1": 0.7}),
    ...     ]
    ... )
    >>> G.add_edge(0, 1, value=3)
    >>> result = nx.alpha_core(
    ...     G, features=["f1"], step_size=0.1, start_epsi=1.0, expo_decay=False
    ... )
    >>> result  # doctest: +SKIP
    {0: {'alpha': 0.2, 'batchID': 3}, 1: {'alpha': 0.7, 'batchID': 9}}
    """
    import numpy as np

    # Make a copy of the graph to avoid modifying the input
    graph = G.copy()

    # Handle empty graph case early
    if graph.number_of_nodes() == 0:
        return {}

    if features is None:
        features = ["all"]

    # 1. Extract numerical node features from the graph; if unavailable, use _compute_default_node_features
    data = _extract_features(graph, features)

    # 2. Compute covariance matrix to be used for all remainder of depth calculations
    matrix = _get_feature_matrix(data)  # Convert data to numeric matrix
    cov = np.cov(matrix.T)

    # 3. Calculate the Mahalanobis depth and add it to the data
    mahal_values = _calculate_mahal_from_center(data, 0, cov)
    for node_id, mahal_val in mahal_values.items():
        data[node_id]["mahal"] = mahal_val

    # 4
    epsi = start_epsi
    # 5
    node = []
    alphaVals = []
    # 6
    batch = []
    # 7
    alpha = 1 - epsi
    # 8
    alphaPrev = alpha
    # 9
    batchID = 0

    # 10
    while graph.number_of_nodes() > 0:
        # 11
        while True:
            depthFound = False  # To simulate do-while loop; used to check if there exists a node with depth >= epsi on current iteration
            # 12
            for node_id, node_data in data.items():
                if node_data["mahal"] >= epsi:
                    depthFound = True
                    # 13
                    node.append(node_id)  # Set node core
                    alphaVals.append(alphaPrev)
                    # 14
                    batch.append(batchID)
                    # 15
                    graph.remove_node(node_id)
            # 16
            batchID += 1

            # 19 Exit condition of do-while loop of # 11
            if graph.number_of_nodes() == 0 or not depthFound:
                break
            # 17
            data = _extract_features(graph, features)  # Recompute node properties
            # 18
            mahal_values = _calculate_mahal_from_center(data, 0, cov)  # Recompute depth
            for node_id, mahal_val in mahal_values.items():
                data[node_id]["mahal"] = mahal_val

        # 20
        alphaPrev = alpha
        # 21
        if expo_decay and graph.number_of_nodes() > 0:  # Exponential decay
            localStepSize = math.ceil(graph.number_of_nodes() * step_size)
            # Sort by mahal values in descending order
            sorted_nodes = sorted(
                data.items(), key=lambda x: x[1]["mahal"], reverse=True
            )
            if localStepSize <= len(sorted_nodes):
                epsi = sorted_nodes[localStepSize - 1][1]["mahal"]
        else:  # step decay
            epsi -= step_size
        # 22
        alpha = 1 - epsi

    # Return results as dictionary
    return {
        node_id: {"alpha": alpha_val, "batchID": batch_id}
        for node_id, alpha_val, batch_id in zip(node, alphaVals, batch)
    }


def _extract_features(graph, features=None):
    """Extract numerical node features from the graph.

    Parameters
    ----------
    graph : NetworkX graph
        A directed graph.
    features : list, optional (default=None)
        A list of feature names to extract. If None or ["all"], uses all
        numerical node attributes or computes default features.

    Returns
    -------
    dict
        Dictionary mapping node IDs to feature dictionaries.
    """
    import numpy as np

    if features is None:
        features = ["all"]

    # Add check for empty feature list
    if not features:
        warnings.warn("No node features found. Using default AlphaCore node features.")
        return _compute_default_node_features(graph)

    # Handle empty graph case
    if graph.number_of_nodes() == 0:
        return {}

    # Get node attributes as dictionary
    node_data = dict(graph.nodes(data=True))

    # Get all features from the first node (assuming all nodes have same attributes)
    if not node_data:
        warnings.warn("No node features found. Using default AlphaCore node features.")
        return _compute_default_node_features(graph)

    # Get all available features
    all_features = set()
    for node_attrs in node_data.values():
        all_features.update(node_attrs.keys())

    # If no features found, use default features
    if not all_features:
        warnings.warn("No node features found. Using default AlphaCore node features.")
        return _compute_default_node_features(graph)

    # Check for numeric features
    numeric_features = set()
    for feature in all_features:
        # Check if feature is numeric for all nodes
        is_numeric = True
        for node_attrs in node_data.values():
            if feature in node_attrs:
                try:
                    float(node_attrs[feature])
                except (ValueError, TypeError):
                    is_numeric = False
                    break
            else:
                is_numeric = False
                break
        if is_numeric:
            numeric_features.add(feature)

    # Handle feature selection
    if features == ["all"]:
        if not numeric_features:
            warnings.warn(
                "No numerical node features found. Using default AlphaCore node features."
            )
            return _compute_default_node_features(graph)
        selected_features = numeric_features
    else:
        # Check for missing features
        missing_features = set(features) - all_features
        if missing_features:
            warnings.warn(
                "No node features found. Using default AlphaCore node features."
            )
            return _compute_default_node_features(graph)

        # Check for non-numeric features
        non_numeric_features = set(features) - numeric_features
        if non_numeric_features:
            warnings.warn(
                f"Features {non_numeric_features} are not numeric. Using default AlphaCore node features."
            )
            return _compute_default_node_features(graph)

        selected_features = set(features)

    # Build result dictionary
    result = {}
    for node_id, node_attrs in node_data.items():
        result[node_id] = {}
        for feature in selected_features:
            result[node_id][feature] = float(node_attrs.get(feature, 0.0))

    return result


def _compute_default_node_features(graph, weight="value"):
    """Compute default structural features for nodes in a directed graph.

    Calculates the following features for each node:
    - In-degree: Number of incoming edges.
    - Out-degree: Number of outgoing edges.
    - In-strength: Sum of weights of incoming edges (or in-degree if no weights).
    - Out-strength: Sum of weights of outgoing edges (or out-degree if no weights).

    Parameters
    ----------
    graph : NetworkX graph
        A directed graph for which node features are computed.
    weight : string, optional (default='value')
        The edge attribute to use as weight for strength calculations.
        If the attribute doesn't exist, falls back to unweighted degree.

    Returns
    -------
    dict
        Dictionary mapping node IDs to feature dictionaries containing:
        - 'inDegree': In-degree of the node.
        - 'outDegree': Out-degree of the node.
        - 'inStrength': Weighted in-degree.
        - 'outStrength': Weighted out-degree.
    """
    # Get degree information using NetworkX methods
    in_degree = dict(graph.in_degree())
    out_degree = dict(graph.out_degree())
    in_strength = dict(graph.in_degree(weight=weight))
    out_strength = dict(graph.out_degree(weight=weight))

    # Build result dictionary
    result = {}
    for node in graph.nodes():
        result[node] = {
            "inDegree": float(in_degree[node]),
            "outDegree": float(out_degree[node]),
            "inStrength": float(in_strength[node]),
            "outStrength": float(out_strength[node]),
        }

    return result


def _get_feature_matrix(data):
    """Convert feature data to numpy matrix for covariance calculation.

    Parameters
    ----------
    data : dict
        Dictionary mapping node IDs to feature dictionaries.

    Returns
    -------
    numpy.ndarray
        Matrix where each row is a node and each column is a feature.
    """
    import numpy as np

    if not data:
        return np.array([])

    # Get feature names from first node
    first_node_data = next(iter(data.values()))
    feature_names = [name for name in first_node_data if name != "mahal"]

    if not feature_names:
        return np.array([])

    # Build matrix
    matrix = []
    for node_data in data.values():
        row = [node_data[feature] for feature in feature_names]
        matrix.append(row)

    return np.array(matrix)


def _calculate_mahal_from_center(data, center, cov):
    """Calculate Mahalanobis depth from a given center.

    Parameters
    ----------
    data : dict
        Dictionary mapping node IDs to feature dictionaries.
    center : float or array
        Center value for Mahalanobis depth calculation.
    cov : array
        Covariance matrix of the data.

    Returns
    -------
    dict
        Dictionary mapping node IDs to Mahalanobis depth values.
    """
    import numpy as np

    matrix = _get_feature_matrix(data)

    # Handle empty or single-feature case
    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        # No features, return zeros
        return dict.fromkeys(data.keys(), 0.0)

    x_minus_center = matrix - center
    x_minus_center_transposed = x_minus_center.T

    # Ensure covariance matrix is at least 2D
    if np.isscalar(cov) or cov.ndim == 0:
        cov = np.array([[cov]])
    elif cov.ndim == 1:
        cov = np.array([cov]).T @ np.array([cov])

    # Try computing the inverse of the covariance matrix; if it fails,
    # fall back to the pseudo-inverse for stability.
    try:
        inv_cov = np.linalg.inv(cov)
    except np.linalg.LinAlgError:
        warnings.warn(
            "Covariance matrix is not invertible, using Moore-Penrose pseudo-inverse instead."
        )
        inv_cov = np.linalg.pinv(cov)

    left = np.dot(x_minus_center, inv_cov)
    mahal = np.dot(left, x_minus_center_transposed)

    mahal_diag = np.diagonal(
        mahal
    )  # Diagonal contains the depth values corresponding to each row from matrix
    mahal_values = np.reciprocal(1 + np.maximum(mahal_diag, 0))  # Ensure stability

    # Return as dictionary mapping node IDs to depth values
    node_ids = list(data.keys())
    return {
        node_id: float(depth_val) for node_id, depth_val in zip(node_ids, mahal_values)
    }
