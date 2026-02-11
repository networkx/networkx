"""
Network backbone extraction algorithms.

Modules
-------
statistical
    disparity_filter, noise_corrected_filter, marginal_likelihood_filter,
    ecm_filter, lans_filter
structural
    global_threshold_filter, strongest_n_ties, high_salience_skeleton,
    metric_backbone, ultrametric_backbone, doubly_stochastic_filter,
    h_backbone, modularity_backbone, planar_maximally_filtered_graph,
    maximum_spanning_tree_backbone
hybrid
    glab_filter
bipartite
    sdsm, fdsm
unweighted
    sparsify, lspar, local_degree
filters
    threshold_filter, fraction_filter, boolean_filter, consensus_backbone
measures
    node_fraction, edge_fraction, weight_fraction, reachability,
    ks_degree, ks_weight, compare_backbones
"""

# Statistical methods
from backbone.statistical import (
    disparity_filter,
    noise_corrected_filter,
    marginal_likelihood_filter,
    ecm_filter,
    lans_filter,
)

# Structural methods
from backbone.structural import (
    global_threshold_filter,
    strongest_n_ties,
    high_salience_skeleton,
    metric_backbone,
    ultrametric_backbone,
    doubly_stochastic_filter,
    h_backbone,
    modularity_backbone,
    planar_maximally_filtered_graph,
    maximum_spanning_tree_backbone,
    neighborhood_overlap,
    jaccard_backbone,
    dice_backbone,
    cosine_backbone,
)

# Hybrid methods
from backbone.hybrid import glab_filter

# Bipartite projection methods
from backbone.bipartite import sdsm, fdsm

# Unweighted methods
from backbone.unweighted import sparsify, lspar, local_degree

# Filtering utilities
from backbone.filters import (
    threshold_filter,
    fraction_filter,
    boolean_filter,
    consensus_backbone,
)

# Evaluation measures
from backbone.measures import (
    node_fraction,
    edge_fraction,
    weight_fraction,
    reachability,
    ks_degree,
    ks_weight,
    compare_backbones,
)

__all__ = [
    # Statistical
    "disparity_filter",
    "noise_corrected_filter",
    "marginal_likelihood_filter",
    "ecm_filter",
    "lans_filter",
    # Structural
    "global_threshold_filter",
    "strongest_n_ties",
    "high_salience_skeleton",
    "metric_backbone",
    "ultrametric_backbone",
    "doubly_stochastic_filter",
    "h_backbone",
    "modularity_backbone",
    "planar_maximally_filtered_graph",
    "maximum_spanning_tree_backbone",
    "neighborhood_overlap",
    "jaccard_backbone",
    "dice_backbone",
    "cosine_backbone",
    # Hybrid
    "glab_filter",
    # Bipartite
    "sdsm",
    "fdsm",
    # Unweighted
    "sparsify",
    "lspar",
    "local_degree",
    # Filters
    "threshold_filter",
    "fraction_filter",
    "boolean_filter",
    "consensus_backbone",
    # Measures
    "node_fraction",
    "edge_fraction",
    "weight_fraction",
    "reachability",
    "ks_degree",
    "ks_weight",
    "compare_backbones",
]
