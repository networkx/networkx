# `networkx.algorithms.backbone` — Network Backbone Extraction

## Summary

This module implements backbone extraction algorithms for weighted, unweighted,
and bipartite projection networks. Backbone extraction reduces dense networks to
sparse subgraphs that preserve structurally important features — multiscale edge
significance, community structure, hub-and-spoke topology — while removing noise
and redundant connections.

The implementation consolidates methods from two open-source packages:

- **netbone** — Yassin, A., Cherifi, H., Seba, H., & Togni, O. (2023). "An
  evaluation tool for backbone extraction techniques in weighted complex
  networks." *Scientific Reports*, 13, 17000.
  https://doi.org/10.1038/s41598-023-42076-3
- **backbone** — Neal, Z. P. (2022). "backbone: An R package to extract network
  backbones." *PLOS ONE*, 17(5), e0269137.
  https://doi.org/10.1371/journal.pone.0269137

---

## Algorithm Reference

### Statistical Methods (`backbone.statistical`)

These methods test edge significance against a null model and assign p-values.

| Function | Description | Reference |
|---|---|---|
| `disparity_filter` | Tests normalised edge weight against a uniform null. The p-value is `1 - (k-1)(1-p)^(k-2)`. For undirected edges, the minimum of both endpoints is used. | Serrano, M. Á., Boguñá, M., & Vespignani, A. (2009). "Extracting the multiscale backbone of complex weighted networks." *PNAS*, 106(16), 6483–6488. https://doi.org/10.1073/pnas.0808904106 |
| `noise_corrected_filter` | Bayesian framework modelling edge weights as binomial outcomes. Computes a z-score measuring standard deviations above the expected weight `E[w] = s_u·s_v/W`. | Coscia, M. & Neffke, F. M. (2017). "Network backboning with noisy data." *Proc. IEEE ICDE*, 425–436. https://doi.org/10.1109/ICDE.2017.100 |
| `marginal_likelihood_filter` | Binomial null model considering both endpoint strengths jointly. P-value via `Binom(s_u, s_v/(W-s_u))`. | Dianati, N. (2016). "Unwinding the hairball graph: Pruning algorithms for weighted complex networks." *Physical Review E*, 93, 012304. https://doi.org/10.1103/PhysRevE.93.012304 |
| `ecm_filter` | Enhanced Configuration Model. Maximum-entropy null preserving expected degree *and* strength sequences via iterative Lagrange multipliers. | Gemmetto, V., Cardillo, A., & Garlaschelli, D. (2017). "Irreducible network backbones: unbiased graph filtering via maximum entropy." arXiv:1706.00230. |
| `lans_filter` | Locally Adaptive Network Sparsification. Nonparametric: uses the empirical CDF of each node's edge weights. No distributional assumptions. | Foti, N. J., Hughes, J. M., & Rockmore, D. N. (2011). "Nonparametric sparsification of complex multiscale networks." *PLoS ONE*, 6(2), e16431. https://doi.org/10.1371/journal.pone.0016431 |

### Structural Methods (`backbone.structural`)

These methods operate on topology and edge weights directly.

| Function | Description | Reference |
|---|---|---|
| `global_threshold_filter` | Retains edges with weight ≥ threshold. Simplest method but ignores local structure. | — |
| `strongest_n_ties` | Each node keeps its *n* strongest edges (OR semantics across endpoints). | — |
| `high_salience_skeleton` | Edge salience = fraction of all shortest-path trees containing that edge. Bimodal distribution near 0 and 1. | Grady, D., Thiemann, C., & Brockmann, D. (2012). "Robust classification of salient links in complex networks." *Nature Communications*, 3, 864. https://doi.org/10.1038/ncomms1847 |
| `metric_backbone` | Edge retained iff its direct distance `1/w` equals the shortest-path distance (sum of distances). | Simas, T., Correia, R. B., & Rocha, L. M. (2021). "The distance backbone of complex networks." *J. Complex Networks*, 9, cnab021. https://doi.org/10.1093/comnet/cnab021 |
| `ultrametric_backbone` | Like metric backbone but using minimax (bottleneck) path distance. | Simas et al. (2021), as above. |
| `doubly_stochastic_filter` | Sinkhorn-Knopp normalisation to a doubly-stochastic matrix. Preserves weight and degree distributions well. | Slater, P. B. (2009). "A two-stage algorithm for extracting the multiscale backbone of complex weighted networks." *PNAS*, 106(26), E66. https://doi.org/10.1073/pnas.0904725106 |
| `h_backbone` | h-index of the weight sequence: keep h edges with weight ≥ h, plus top-h bridging edges by betweenness. | Zhang, R. J., Stanley, H. E., & Ye, F. Y. (2018). "Extracting h-backbone as a core structure in weighted networks." *Scientific Reports*, 8, 14356. https://doi.org/10.1038/s41598-018-32430-1 |
| `modularity_backbone` | Node vitality = modularity change when node is removed. Filters nodes by contribution to community structure. | Rajeh, S., Savonnet, M., Leclercq, E., & Cherifi, H. (2022). "Modularity-based backbone extraction in weighted complex networks." *NetSci-X 2022*, 67–79. |
| `planar_maximally_filtered_graph` | Greedily adds edges from heaviest to lightest while maintaining planarity. At most 3(n−2) edges. | Tumminello, M., Aste, T., Di Matteo, T., & Mantegna, R. N. (2005). "A tool for filtering information in complex systems." *PNAS*, 102(30), 10421–10426. https://doi.org/10.1073/pnas.0500298102 |
| `maximum_spanning_tree_backbone` | Maximum weight spanning tree. Connected, n−1 edges, maximum total weight. | Kruskal, J. B. (1956). "On the shortest spanning subtree of a graph." *Proc. AMS*, 7(1), 48–50. |
### Proximity Methods (`backbone.proximity`)

These methods score each existing edge by the topological proximity (similarity)
of its endpoints. They identify *structurally embedded* edges — edges between
nodes that share many neighbors — versus *bridging* edges that connect otherwise
separate parts of the network. All methods work on both weighted and unweighted
graphs (weights are ignored; only topology matters) and support directed graphs
using the out-neighbor convention.

The methods are organized into **local** indices (based on immediate neighborhood
structure) and **quasi-local** indices (incorporating short-range path information).

#### Local Proximity Indices

| Function | Formula | Description | Reference |
|---|---|---|---|
| `neighborhood_overlap` | `\|N(u) ∩ N(v)\|` | Raw count of shared neighbors. Unnormalized; use a normalized variant for degree-corrected scoring. | — |
| `jaccard_backbone` | `n_uv / (k_u + k_v - n_uv)` | Jaccard similarity [0, 1]. Strictest normaliser — edges score high only when endpoints share many neighbors relative to their combined neighborhood. Bridge edges score 0. | Jaccard, P. (1901). "Distribution de la flore alpine dans le bassin des Dranses et dans quelques régions voisines." *Bulletin de la Société Vaudoise des Sciences Naturelles*, 37, 241–272. |
| `dice_backbone` | `2·n_uv / (k_u + k_v)` | Dice / Sørensen coefficient [0, 1]. Always ≥ Jaccard for the same edge. Gives more credit to overlap between low-degree nodes. | Dice, L. R. (1945). "Measures of the amount of ecologic association between species." *Ecology*, 26(3), 297–302. https://doi.org/10.2307/1932409 |
| `cosine_backbone` | `n_uv / √(k_u · k_v)` | Cosine / Salton index [0, 1]. Uses the geometric mean of degrees as denominator. Penalises degree disparity less than Jaccard but more than Dice. | Salton, G. & McGill, M. J. (1983). *Introduction to Modern Information Retrieval*. McGraw-Hill. |
| `hub_promoted_index` | `n_uv / min(k_u, k_v)` | Hub Promoted Index [0, 1]. Normalises by the smaller degree, so edges incident to hubs are promoted. | Ravasz, E., Somera, A. L., Mongru, D. A., Oltvai, Z. N., & Barabási, A.-L. (2002). "Hierarchical organization of modularity in metabolic networks." *Science*, 297(5586), 1551–1555. https://doi.org/10.1126/science.1073374 |
| `hub_depressed_index` | `n_uv / max(k_u, k_v)` | Hub Depressed Index [0, 1]. Normalises by the larger degree, so edges between high-degree nodes are penalised. Always ≤ HPI. | Zhou, T., Lü, L., & Zhang, Y.-C. (2009). "Predicting missing links via local information." *European Physical Journal B*, 71, 623–630. https://doi.org/10.1140/epjb/e2009-00335-8 |
| `lhn_local_index` | `n_uv / (k_u · k_v)` | Leicht–Holme–Newman local similarity index. Normalises by the product of degrees, penalising high-degree node pairs more aggressively than any other local index. | Leicht, E. A., Holme, P., & Newman, M. E. J. (2006). "Vertex similarity in networks." *Physical Review E*, 73, 026120. https://doi.org/10.1103/PhysRevE.73.026120 |
| `preferential_attachment_score` | `k_u · k_v` | Preferential attachment score. Unlike all other indices, this does **not** use common neighbors — it scores edges purely by the product of endpoint degrees. High-degree node pairs score highest. | Barabási, A.-L. & Albert, R. (1999). "Emergence of scaling in random networks." *Science*, 286(5439), 509–512. https://doi.org/10.1126/science.286.5439.509 |
| `adamic_adar_index` | `Σ_{w ∈ N(u)∩N(v)} 1/log(k_w)` | Adamic–Adar index. Weights each common neighbor by the inverse of its log-degree, giving more credit to rare shared neighbors. | Adamic, L. A. & Adar, E. (2003). "Friends and neighbors on the Web." *Social Networks*, 25(3), 211–230. https://doi.org/10.1016/S0378-8733(03)00009-1 |
| `resource_allocation_index` | `Σ_{w ∈ N(u)∩N(v)} 1/k_w` | Resource allocation index. Like Adamic–Adar but penalises high-degree intermediaries more strongly (1/k instead of 1/log k). | Zhou et al. (2009), as above. |

#### Quasi-Local Proximity Indices

| Function | Formula | Description | Reference |
|---|---|---|---|
| `graph_distance_proximity` | `1 / d(u, v)` | Reciprocal of shortest-path distance. For existing edges this is always 1.0 (since adjacent nodes have distance 1). Most useful as a baseline or when extended to non-edges. | Lü, L. & Zhou, T. (2011). "Link prediction in complex networks: A survey." *Physica A*, 390(6), 1150–1170. https://doi.org/10.1016/j.physa.2010.11.027 |
| `local_path_index` | `\|A²(u,v)\| + ε·\|A³(u,v)\|` | Local path index combining second-order paths (common neighbors) and third-order paths, weighted by parameter ε. Captures local clustering beyond immediate neighbors. | Lü, L., Jin, C.-H., & Zhou, T. (2009). "Similarity index based on local random walk and length of shortest paths." *Physical Review E*, 80, 046122. https://doi.org/10.1103/PhysRevE.80.046122 |

**Key relationships among local indices.** For any edge (u, v) with at least one
common neighbor, the following inequalities hold:

- HDI ≤ Jaccard ≤ Cosine ≤ Dice ≤ HPI
- LHN ≤ HDI (since k_u · k_v ≥ max(k_u, k_v) when both degrees > 1)

All common-neighbor–based indices (Jaccard, Dice, cosine, HPI, HDI, LHN,
Adamic–Adar, resource allocation) return 0 for bridge edges with no shared
neighbors. Preferential attachment is the exception: it depends only on
endpoint degrees.

### Hybrid Methods (`backbone.hybrid`)

| Function | Description | Reference |
|---|---|---|
| `glab_filter` | Globally and Locally Adaptive Backbone. Combines edge betweenness centrality (global involvement) with a degree-dependent significance test. | Zhang, X., Zhang, Z., Zhao, H., Wang, Q., & Zhu, J. (2014). "Extracting the globally and locally adaptive backbone of complex networks." *PLoS ONE*, 9(6), e100428. https://doi.org/10.1371/journal.pone.0100428 |

### Bipartite Projection Methods (`backbone.bipartite`)

| Function | Description | Reference |
|---|---|---|
| `sdsm` | Stochastic Degree Sequence Model. Constrains random bipartite networks to match row/column sums on average. Normal approximation for p-values. | Neal, Z. P. (2014). "The backbone of bipartite projections." *Social Networks*, 39, 84–97. https://doi.org/10.1016/j.socnet.2014.06.001 |
| `fdsm` | Fixed Degree Sequence Model. Monte Carlo with exact degree preservation via Curveball swaps. | Neal, Z. P., Domagalski, R., & Sagan, B. (2021). "Comparing alternatives to the fixed degree sequence model." *Scientific Reports*, 11, 23929. https://doi.org/10.1038/s41598-021-03238-3 |

### Unweighted Methods (`backbone.unweighted`)

| Function | Description | Reference |
|---|---|---|
| `sparsify` | Generic framework: score → normalise → filter → connect. Supports Jaccard, degree, triangle, quadrangle, and random scoring. | Neal (2022), as above. |
| `lspar` | Local Sparsification. Jaccard scoring + rank normalisation + degree filtering. Best for preserving community structure. | Satuluri, V., Parthasarathy, S., & Ruan, Y. (2011). "Local graph sparsification for scalable clustering." *ACM SIGMOD*, 721–732. https://doi.org/10.1145/1989323.1989399 |
| `local_degree` | Degree scoring + rank normalisation + degree filtering. Best for preserving hub-and-spoke structure. | Hamann, M., Lindner, G., Meyerhenke, H., Staudt, C. L., & Wagner, D. (2016). "Structure-preserving sparsification methods for social networks." *Social Network Analysis and Mining*, 6(1), 22. https://doi.org/10.1007/s13278-016-0332-2 |

### Filtering Utilities (`backbone.filters`)

| Function | Description |
|---|---|
| `threshold_filter` | Retain edges/nodes with score above or below a threshold. |
| `fraction_filter` | Retain the top or bottom fraction of edges/nodes by score. |
| `boolean_filter` | Retain edges where a boolean attribute is True. |
| `consensus_backbone` | Intersection of multiple backbone graphs. |

### Evaluation Measures (`backbone.measures`)

| Function | Description |
|---|---|
| `node_fraction` | Fraction of original nodes with edges in the backbone. |
| `edge_fraction` | Fraction of original edges preserved. |
| `weight_fraction` | Fraction of total edge weight preserved. |
| `reachability` | Fraction of node pairs that can communicate. |
| `ks_degree` | Kolmogorov-Smirnov statistic between degree distributions. |
| `ks_weight` | Kolmogorov-Smirnov statistic between weight distributions. |
| `compare_backbones` | Compare multiple backbones across any set of measures. |

---

## Tutorial: Backbone Extraction on Les Misérables

The Les Misérables co-occurrence network is bundled with NetworkX. Each node
is a character; each edge weight is the number of chapters in which two
characters appear together.

```python
import networkx as nx
from backbone.statistical import disparity_filter, noise_corrected_filter, lans_filter
from backbone.structural import (
    global_threshold_filter,
    strongest_n_ties,
    high_salience_skeleton,
    metric_backbone,
    doubly_stochastic_filter,
    h_backbone,
    planar_maximally_filtered_graph,
    maximum_spanning_tree_backbone,
)
from backbone.proximity import (
    jaccard_backbone,
    cosine_backbone,
    adamic_adar_index,
    hub_promoted_index,
)
from backbone.hybrid import glab_filter
from backbone.filters import threshold_filter, fraction_filter, consensus_backbone
from backbone.measures import (
    edge_fraction,
    weight_fraction,
    reachability,
    ks_degree,
    compare_backbones,
)

# Load the network
G = nx.les_miserables_graph()
print(f"Les Misérables: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
```

### 1. Statistical backbone: Disparity Filter

```python
# Score every edge with a p-value
G_disp = disparity_filter(G)

# Retain only edges significant at alpha = 0.05
bb_disp = threshold_filter(G_disp, "disparity_pvalue", 0.05, "below")
print(f"Disparity (α=0.05): {bb_disp.number_of_edges()} edges "
      f"({edge_fraction(G, bb_disp):.1%} of original)")
```

### 2. Structural backbones

```python
# Global threshold: keep edges with weight >= 5
bb_thresh = global_threshold_filter(G, threshold=5)

# Each character keeps their 2 strongest relationships
bb_strong = strongest_n_ties(G, n=2)

# Salience skeleton: which edges appear in many shortest-path trees?
G_sal = high_salience_skeleton(G)
bb_sal = threshold_filter(G_sal, "salience", 0.5, "above")

# Metric backbone: edges that are actual shortest paths
bb_metric = metric_backbone(G)

# Maximum spanning tree
bb_mst = maximum_spanning_tree_backbone(G)

# h-backbone
bb_h = h_backbone(G)

# PMFG: maximally dense planar subgraph
bb_pmfg = planar_maximally_filtered_graph(G)
```

### 3. Hybrid backbone: GLAB

```python
G_glab = glab_filter(G, c=0.5)
bb_glab = threshold_filter(G_glab, "glab_pvalue", 0.1, "below")
```

### 4. Proximity metrics: embedded vs. bridging edges

Proximity methods score edges by the topological similarity of their
endpoints — how many neighbors two characters share, weighted by various
normalisation schemes. Edges with high scores connect characters embedded
in the same social circle; edges with low scores bridge otherwise separate
groups.

```python
from backbone.proximity import (
    jaccard_backbone,
    cosine_backbone,
    adamic_adar_index,
    hub_promoted_index,
)

# Score every edge by Jaccard similarity of endpoint neighborhoods
G_jac = jaccard_backbone(G)

# Keep only structurally embedded edges (Jaccard >= 0.3)
bb_embedded = threshold_filter(G_jac, "jaccard", 0.3, "above")
print(f"Embedded backbone: {bb_embedded.number_of_edges()} edges "
      f"({edge_fraction(G, bb_embedded):.1%} of original)")

# Or keep only bridging edges (Jaccard = 0, no common neighbors)
bb_bridges = threshold_filter(G_jac, "jaccard", 0.01, "below")
print(f"Bridge edges: {bb_bridges.number_of_edges()} edges")

# Cosine similarity offers a softer normalisation
G_cos = cosine_backbone(G)
bb_cosine = threshold_filter(G_cos, "cosine", 0.4, "above")

# Adamic-Adar weights common neighbors by rarity (1/log(degree))
G_aa = adamic_adar_index(G)
bb_aa = fraction_filter(G_aa, "adamic_adar", 0.3, ascending=False)

# Hub Promoted Index favours edges incident to hubs
G_hpi = hub_promoted_index(G)
bb_hpi = threshold_filter(G_hpi, "hpi", 0.3, "above")
```

### 6. Comparing backbones

```python
backbones = {
    "disparity_0.05": bb_disp,
    "threshold_5": bb_thresh,
    "strongest_2": bb_strong,
    "salience_0.5": bb_sal,
    "metric": bb_metric,
    "mst": bb_mst,
    "h_backbone": bb_h,
    "pmfg": bb_pmfg,
    "glab_0.1": bb_glab,
    "jaccard_0.3": bb_embedded,
    "cosine_0.4": bb_cosine,
    "adamic_adar_30%": bb_aa,
    "hpi_0.3": bb_hpi,
}

results = compare_backbones(
    G, backbones,
    measures=[edge_fraction, weight_fraction, reachability],
)

print(f"{'Method':<20} {'Edges':>8} {'Weight':>8} {'Reach':>8}")
print("-" * 48)
for name, metrics in results.items():
    print(f"{name:<20} {metrics['edge_fraction']:>7.1%} "
          f"{metrics['weight_fraction']:>7.1%} "
          f"{metrics['reachability']:>7.1%}")
```

### 7. Consensus backbone

```python
# Which edges do the disparity filter AND the salience skeleton agree on?
bb_consensus = consensus_backbone(bb_disp, bb_sal)
print(f"Consensus: {bb_consensus.number_of_edges()} edges")
```

---

## Evaluation of `al1yass2n/structural-backbone-methods-comparison`

### Overview

The repository [al1yass2n/structural-backbone-methods-comparison](https://github.com/al1yass2n/structural-backbone-methods-comparison)
is the companion code for:

> Yassin, A., Cherifi, H., Seba, H., & Togni, O. (2025). "Exploring weighted
> network backbone extraction: A comparative analysis of structural techniques."
> *PLOS ONE*, 20(5), e0322298. https://doi.org/10.1371/journal.pone.0322298

The repo provides scripts and data for comparing **eight structural backbone
methods** across **33 real-world networks** spanning social, biological,
infrastructure, and economic domains.

### Repository structure

```
├── Data/               # 33 real-world network datasets
├── Results/            # Pre-computed backbone outputs
├── Figures/            # Publication figures
├── run backbone methods.py         # Extracts backbones using netbone
├── similarity analysis JI.py       # Jaccard similarity between methods
├── similarity analysis OC.py       # Overlap Coefficient between methods
├── edge correlation analysis.py    # Point-biserial correlations
├── properties analysis.py          # Global backbone property comparison
├── distribution analysis.py        # KS tests on degree/weight distributions
├── combine methods.py              # Combines and exports results
└── README.md
```

### Methods evaluated

The paper evaluates these structural methods (all available in our module):

| Abbreviation | Our function | Category |
|---|---|---|
| MSP | `maximum_spanning_tree_backbone` | Single-structure |
| PLAM | *(primary linkage analysis; essentially `strongest_n_ties(G, n=1)`)* | Single-structure |
| UMB | `ultrametric_backbone` | Single-structure |
| MB | `metric_backbone` | Single-structure |
| HSS | `high_salience_skeleton` | Score-based |
| DS | `doubly_stochastic_filter` | Score-based |
| HB | `h_backbone` | Score-based |
| PMFG | `planar_maximally_filtered_graph` | Single-structure |

### Key findings relevant to our implementation

The paper establishes a **hierarchical containment** among structural methods:

```
PLAM ⊂ MSP ⊂ UMB ⊂ MB
```

That is, the primary linkage analysis backbone is always a subgraph of the MSP,
which is always a subgraph of the ultrametric backbone, which is always a
subgraph of the metric backbone. Our implementation preserves this hierarchy.

Additional findings that inform testing and method selection guidance:

1. **Doubly Stochastic Filter** best preserves weight and degree distributions,
   connectivity, and transitivity. It is the recommended default when the goal
   is faithful network simplification.
2. **Metric Backbone** and **PMFG** guarantee complete node preservation and
   maintain high reachability.
3. **h-Backbone** prioritises high-weight edges aggressively but can disrupt
   connectivity — users should check `reachability()` after extraction.
4. **High Salience Skeleton** captures multi-scale structure but may disconnect
   the network at moderate thresholds.

### What we adopt from the repo

1. **Evaluation metrics**: The paper's comparison framework (edge/node/weight
   fractions, reachability, KS degree/weight statistics, Jaccard similarity)
   maps directly onto our `backbone.measures` module. We implement all of these.

2. **Test cases**: The hierarchical containment property `PLAM ⊂ MSP ⊂ UMB ⊂ MB`
   should be verified as a property-based test. Our test suite includes
   subgraph-property tests for all structural methods.

3. **Method selection guidance**: The paper's findings inform the docstring
   guidance in each function (e.g., "doubly stochastic filter excels at
   preserving weight and degree distributions").

4. **Dataset scope**: While we cannot bundle 33 external datasets, the paper
   validates our implementations across diverse network types. Our tests use
   NetworkX's bundled datasets (Les Misérables, Karate Club) plus synthetic
   graphs covering the relevant topologies.

### What we do not adopt

1. **Script-based workflow**: The repo uses standalone `.py` scripts with
   hardcoded paths and `netbone` as a dependency. Our module integrates
   natively into NetworkX with no external dependencies.
2. **Visualization code**: The publication figures use matplotlib with custom
   styling. Gallery examples are the appropriate NetworkX mechanism for this.
3. **Primary Linkage Analysis as a separate function**: The paper treats PLAM as
   a distinct method, but it is equivalent to `strongest_n_ties(G, n=1)`. We
   document this equivalence rather than adding a redundant function.

---

## Design Principles

Following NetworkX conventions:

- **NetworkX-native I/O**: All functions accept and return `nx.Graph` or
  `nx.DiGraph`.
- **Edge attribute convention**: Scores and p-values are stored as edge
  attributes so users can inspect intermediate results.
- **Separation of scoring and filtering**: Methods compute scores; users apply
  filters explicitly via `threshold_filter`, `fraction_filter`, or
  `boolean_filter`.
- **No new dependencies**: Uses only `numpy` and `scipy` (already NetworkX
  dependencies).
- **NumPy-style docstrings**: All functions follow the
  [numpydoc standard](https://numpydoc.readthedocs.io/en/latest/format.html).
- **`not_implemented_for` decorator**: Functions that require undirected graphs
  raise `NetworkXError` for directed input (following the pattern used
  throughout `networkx.algorithms`).
- **Chicago-style citations**: All references in docstrings use DOI links
  following NetworkX's contributor guidelines.

---

## Testing

```bash
# Run all backbone tests
pytest backbone/tests/ -v

# 261 tests across 10 test modules covering:
#   - All 30+ backbone extraction and proximity scoring algorithms
#   - Directed and undirected weighted graphs
#   - Statistical, structural, proximity, hybrid, bipartite, and unweighted methods
#   - 12 proximity indices with value verification and cross-method invariants
#   - Filtering utilities and evaluation measures
#   - Edge cases (empty graphs, single nodes, self-loops)
#   - End-to-end pipelines and cross-method comparisons
#   - Monotonicity and containment properties
```

Tests are organized by category:

| Test file | Coverage |
|---|---|
| `test_statistical.py` | disparity, noise-corrected, marginal likelihood, ECM, LANS filters |
| `test_structural.py` | threshold, strongest-n, salience, metric/ultrametric, doubly stochastic, h-backbone, modularity, PMFG, MST |
| `test_proximity.py` | All 12 proximity indices: neighborhood overlap, Jaccard, Dice, cosine, HPI, HDI, LHN, PA, Adamic–Adar, resource allocation, graph distance, local path index |
| `test_filters.py` | threshold, fraction, boolean, consensus filters |
| `test_measures.py` | node/edge/weight fractions, reachability, KS statistics, compare_backbones |
| `test_hybrid.py` | GLAB filter |
| `test_bipartite.py` | SDSM, FDSM |
| `test_unweighted.py` | sparsify, lspar, local_degree |
| `test_integration.py` | End-to-end pipelines, monotonicity, edge cases, smoke tests |
| `conftest.py` | Shared fixtures (two-cluster, star, path, triangle, complete, disconnected) |

Test fixtures include hand-crafted graphs with known structure (two-cluster
barbell, star, path, triangle, complete uniform, disconnected components) and
synthetic graphs for smoke tests.

---

## Attribution

All algorithms are attributed to their original papers in function docstrings.
Implementation draws from:

- **netbone**: Yassin, A. et al. (2023). *Scientific Reports*, 13, 17000.
  CC BY 4.0. https://gitlab.liris.cnrs.fr/coregraphie/netbone
- **backbone (R)**: Neal, Z. P. (2022). *PLOS ONE*, 17(5), e0269137.
  GPL-3.0. https://github.com/zpneal/backbone

The comparative evaluation framework is informed by:

- Yassin, A., Cherifi, H., Seba, H., & Togni, O. (2025). "Exploring weighted
  network backbone extraction: A comparative analysis of structural techniques."
  *PLOS ONE*, 20(5), e0322298. https://doi.org/10.1371/journal.pone.0322298
