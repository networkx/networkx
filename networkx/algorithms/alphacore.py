"""AlphaCore algorithm for node ranking in a directed network.

The algorithm iteratively computes a node ranking based on a feature set
using the Mahalanobis data depth function at the origin.
"""

import math
import warnings

import numpy as np
import pandas as pd

import networkx as nx

__all__ = ["alpha_core"]


@nx.utils.not_implemented_for("undirected", "multigraph")
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
    pandas.DataFrame
        A DataFrame with columns 'nodeID', 'alpha', and 'batchID'.

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
    >>> df = nx.alpha_core(
    ...     G, features=["f1"], step_size=0.1, start_epsi=1.0, expo_decay=False
    ... )
    >>> df
       nodeID  alpha  batchID
    0       0    0.9        0
    1       1    0.9        0
    """
    # Explicitly check if the graph is undirected or a multigraph
    if not G.is_directed():
        raise nx.NetworkXNotImplemented(
            "alpha_core is not implemented for undirected graphs."
        )
    if G.is_multigraph():
        raise nx.NetworkXNotImplemented(
            "alpha_core is not implemented for multigraphs."
        )

    # Make a copy of the graph to avoid modifying the input
    graph = G.copy()

    # Handle empty graph case early
    if graph.number_of_nodes() == 0:
        return pd.DataFrame(columns=["nodeID", "alpha", "batchID"])

    if features is None:
        features = ["all"]

    # 1. Extract numerical node features from the graph; if unavailable, use _compute_node_features
    data = _extract_features(graph, features)

    # 2. Compute covariance matrix to be used for all remainder of depth calculations
    matrix = data.drop(
        "nodeID", axis=1
    )  # Convert dataframe to numeric matrix by removing first column
    cov = np.cov(matrix.values.T)

    # 3. Calculate the Mahalanobis depth and add it to the respective row of the dataframe
    data["mahal"] = _calculate_mahal_from_center(data, 0, cov)

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
            for row in data.itertuples():
                if row.mahal >= epsi:
                    depthFound = True
                    # 13
                    node.append(row.nodeID)  # Set node core
                    alphaVals.append(alphaPrev)
                    # 14
                    batch.append(batchID)
                    # 15
                    graph.remove_node(row.nodeID)
            # 16
            batchID += 1

            # 19 Exit condition of do-while loop of # 11
            if graph.number_of_nodes() == 0 or not depthFound:
                break
            # 17
            data = _extract_features(graph, features)  # Recompute node properties
            # 18
            data["mahal"] = _calculate_mahal_from_center(
                data, 0, cov
            )  # Recompute depth

        # 20
        alphaPrev = alpha
        # 21
        if expo_decay and graph.number_of_nodes() > 0:  # Exponential decay
            localStepSize = math.ceil(graph.number_of_nodes() * step_size)
            data = data.sort_values(ascending=False, by=["mahal"])
            epsi = data.iloc[localStepSize - 1]["mahal"]
        else:  # step decay
            epsi -= step_size
        # 22
        alpha = 1 - epsi

    return pd.DataFrame({"nodeID": node, "alpha": alphaVals, "batchID": batch})


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
    pandas.DataFrame
        DataFrame containing extracted numerical node features.
    """
    if features is None:
        features = ["all"]

    all_features = set()
    numeric_features = set()
    selected_features = set()
    data = {}

    for node_id, attributes in graph.nodes(data=True):
        for key, value in attributes.items():
            all_features.add(key)  # Track all available features
            if isinstance(value, int | float):
                numeric_features.add(key)  # Track only numeric features

    # Determine the features to extract
    if features == ["all"]:
        if not numeric_features:
            warnings.warn(
                "No numerical node features found. Reverting to default AlphaCore node features."
            )
            return _compute_node_features(graph)
        selected_features = numeric_features  # Use all numeric features
    else:
        for feature in features:
            if feature not in all_features:
                print(f"Debug: Available features: {all_features}")
                raise ValueError(
                    f"Feature '{feature}' not found in graph nodes. Please check your graph."
                )
            if feature in numeric_features:
                selected_features.add(feature)

    if not selected_features:
        warnings.warn(
            "None of the selected features contain numerical values. Reverting to default AlphaCore node features."
        )
        return _compute_node_features(graph)

    # Extract feature values for each node
    for node_id, attributes in graph.nodes(data=True):
        node_features = {}
        for feature in selected_features:
            if feature in attributes:
                node_features[feature] = attributes.get(feature)
        data[node_id] = node_features

    return (
        pd.DataFrame.from_dict(data, orient="index")
        .reset_index()
        .rename(columns={"index": "nodeID"})
    )


def _compute_node_features(graph):
    """Compute default node features for a graph.

    Parameters
    ----------
    graph : NetworkX graph
        A directed graph.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing computed node features.
    """
    nodeID = []
    inDegree = []
    outDegree = []
    inStrength = []
    outStrength = []
    for node in graph:
        nodeID.append(node)
        inDegree.append(graph.in_degree(node))
        outDegree.append(graph.out_degree(node))
        inStrength.append(graph.in_degree(node, "value"))
        outStrength.append(graph.out_degree(node, "value"))

    # Currently adding inDegree, outDegree, inStrength, and outStrength to dataframe
    df = pd.DataFrame(
        {
            "nodeID": nodeID,
            "inDegree": inDegree,
            "outDegree": outDegree,
            "inStrength": inStrength,
            "outStrength": outStrength,
        }
    )
    return df


def _calculate_mahal_from_center(data, center, cov):
    """Calculate Mahalanobis depth from a given center.

    Parameters
    ----------
    data : pandas.DataFrame
        DataFrame where each row is a node and columns are features.
    center : float or array
        Center value for Mahalanobis depth calculation.
    cov : array
        Covariance matrix of the data.

    Returns
    -------
    array
        Array containing Mahalanobis depth of each node.
    """
    matrix = data.drop(
        "nodeID", axis=1
    )  # Convert dataframe to numeric matrix by removing first column containing nodeID

    # Handle empty or single-feature case
    if matrix.shape[1] == 0:
        # No features, return zeros
        return np.zeros(matrix.shape[0])

    x_minus_center = matrix.values - center
    x_minus_center_transposed = x_minus_center.T

    # Ensure covariance matrix is at least 2D
    if np.isscalar(cov) or cov.ndim == 0:
        cov = np.array([[cov]])
    elif cov.ndim == 1:
        cov = np.array([cov]).T @ np.array([cov])

    # Try computing the inverse of the covariance matrix; if it fails, fall back to the pseudo-inverse for stability.
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
    return np.reciprocal(1 + np.maximum(mahal_diag, 0))  # Ensure stability
