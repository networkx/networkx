"""Neural Overlapping Community Detection (NOCD)."""

from collections import defaultdict

import networkx as nx
from networkx.utils import py_random_state

__all__ = ["nocd_communities"]


def _missing_ml_extra(exc: ImportError) -> nx.NetworkXError:
    return nx.NetworkXError(
        "nocd_communities requires optional packages "
        "torch and torch_geometric (and scipy/numpy). "
        f"Import failed: {exc}"
    )


def _configure_ml_rng(random_state):
    """Align torch/numpy RNG with NetworkX ``py_random_state`` handling."""
    import random

    import numpy as np

    if random_state is None or random_state is random._inst:
        return

    if isinstance(random_state, random.Random):
        ml_seed = random_state.randint(0, 2**31 - 1)
    else:
        ml_seed = random_state.randint(0, 2**31 - 1)

    import torch

    torch.manual_seed(ml_seed)
    np.random.seed(ml_seed % 2**32)


def _as_undirected(G):
    if G.is_directed():
        return G.to_undirected(as_view=False)
    return G


def _graph_to_csr(G, weight="weight"):
    import numpy as np

    nodelist = list(G.nodes())
    node_to_idx = {node: i for i, node in enumerate(nodelist)}
    idx_to_node = dict(enumerate(nodelist))
    adjacency_csr = nx.to_scipy_sparse_array(
        G,
        nodelist=nodelist,
        weight=weight,
        format="csr",
        dtype=np.float32,
    )
    return adjacency_csr, node_to_idx, idx_to_node


def _affiliations_to_membership(affiliations, node_to_idx, threshold):
    import numpy as np

    membership = {}
    for node_id, node_idx in node_to_idx.items():
        node_affiliations = affiliations[node_idx]
        community_indices = np.where(node_affiliations > threshold)[0].tolist()
        if not community_indices:
            community_indices = [int(np.argmax(node_affiliations))]
        membership[node_id] = community_indices
    return membership


def _membership_to_communities(membership):
    comm_nodes = defaultdict(set)
    for node, comm_ids in membership.items():
        for cid in comm_ids:
            comm_nodes[cid].add(node)
    for nodes in comm_nodes.values():
        if nodes:
            yield frozenset(nodes)


@py_random_state("seed")
@nx._dispatchable(edge_attrs="weight")
def nocd_communities(
    G,
    *,
    num_communities=10,
    hidden_dim=128,
    dropout=0.5,
    lr=1e-3,
    weight_decay=1e-2,
    batch_size=500,
    epochs=5000,
    patience_epochs=5,
    eval_frequency=50,
    threshold=0.5,
    device="auto",
    checkpoint_dir=None,
    weight="weight",
    seed=None,
):
    """Find overlapping communities with NOCD [1]_.

    This function trains a graph convolutional model on the adjacency structure
    of `G` and returns hard overlapping communities by thresholding learned
    affiliation scores.

    Requires optional dependencies ``torch``, ``torch_geometric``, ``numpy``,
    and ``scipy``.

    Parameters
    ----------
    G : NetworkX graph
        The graph must contain at least one edge. Directed graphs are
        converted to undirected for training.

    num_communities : int
        Number of overlapping communities to learn.

    hidden_dim : int
        Hidden dimension of the graph convolutional network.

    dropout : float
        Dropout rate during training.

    lr : float
        Adam learning rate.

    weight_decay : float
        Adam L2 weight decay.

    batch_size : int
        Mini-batch size for the Bernoulli-Poisson loss (paper parameter S).

    epochs : int
        Maximum training epochs.

    patience_epochs : int
        Early stopping patience measured in evaluation periods (each period
        spans ``eval_frequency`` epochs).

    eval_frequency : int
        Evaluate full loss every this many epochs for early stopping.

    threshold : float
        Affiliation scores above this value assign a node to a community.

    device : str
        ``"auto"``, ``"cpu"``, or ``"cuda"``.

    checkpoint_dir : str, optional
        If given, save the best model checkpoint to this directory.

    weight : string or None, optional (default="weight")
        Edge attribute used as weight when building the adjacency matrix.

    seed : integer, random_state, or None (default)
        Indicator of random number generation state for reproducibility.

    Yields
    ------
    frozenset
        A set of nodes belonging to one overlapping community.

    Raises
    ------
    NetworkXError
        If `G` has no edges, parameters are invalid, or optional ML
        dependencies are missing.

    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> comms = list(
    ...     nx.community.nocd_communities(
    ...         G,
    ...         num_communities=4,
    ...         epochs=100,
    ...         eval_frequency=25,
    ...         patience_epochs=2,
    ...         seed=0,
    ...     )
    ... )  # doctest: +SKIP
    >>> nx.community.is_cover(G, comms)  # doctest: +SKIP
    True

    Notes
    -----
    NOCD learns soft community affiliations; ``threshold`` converts them into
    hard overlapping communities for the yielded frozensets.

    References
    ----------
    .. [1] Oleksandr Shchur and Stephan Günnemann.
       Overlapping Community Detection with Graph Neural Networks.
       Deep Learning on Graphs Workshop, KDD (2019).
       https://arxiv.org/abs/1909.12201

    See Also
    --------
    :any:`k_clique_communities`
    """
    if num_communities < 1:
        raise nx.NetworkXError("num_communities must be at least 1.")
    if G.number_of_edges() == 0:
        raise nx.NetworkXError("Graph must have at least one edge.")

    try:
        import torch

        from networkx.algorithms.community._nocd import (
            CSRGraphDataset,
            NOCDTrainer,
            ProductionNOCD,
        )
    except ImportError as exc:
        raise _missing_ml_extra(exc) from exc

    _configure_ml_rng(seed)

    subgraph = _as_undirected(G)
    adjacency_csr, node_to_idx, _idx_to_node = _graph_to_csr(subgraph, weight=weight)
    dataset = CSRGraphDataset(
        adjacency_csr=adjacency_csr, node_features=None, validate=True
    )

    model = ProductionNOCD(
        input_dim=dataset.feature_dim,
        num_communities=num_communities,
        hidden_dim=hidden_dim,
        dropout=dropout,
    )
    trainer = NOCDTrainer(
        model=model,
        dataset=dataset,
        lr=lr,
        weight_decay=weight_decay,
        device=device,
        batch_size=batch_size,
    )

    trainer.train(
        epochs=epochs,
        patience_epochs=patience_epochs,
        eval_frequency=eval_frequency,
        checkpoint_dir=checkpoint_dir,
    )

    data = dataset.to_pyg_data()
    model.eval()
    with torch.no_grad():
        affiliations = model(data.x, data.edge_index).cpu().numpy()

    membership = _affiliations_to_membership(affiliations, node_to_idx, threshold)
    yield from _membership_to_communities(membership)
