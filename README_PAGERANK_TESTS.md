# PageRank Property-Based Tests for NetworkX

## Overview

This contribution adds 5 property-based test cases for the `nx.pagerank()` algorithm to the existing test suite at `networkx/algorithms/link_analysis/tests/test_pagerank.py`.

These tests verify **mathematical invariants** of PageRank that hold across various graph structures, rather than checking against hardcoded expected values on a single fixed graph.

## PageRank — Quick Background

PageRank models a random surfer on a directed graph. At each step, the surfer either:
- **Follows an outgoing link** (probability = α, default 0.85)
- **Teleports** to a random node (probability = 1 − α)

The PageRank of a node is its steady-state visit probability:

```
PR(v) = (1 − α) / N  +  α × Σ [ PR(u) / out-degree(u) ]   for all u → v
```

Key properties: all ranks sum to 1 (probability distribution), every rank is non-negative, and more incoming edges from important nodes means higher rank.

## What NetworkX Already Tests

| Aspect | Covered? |
|--------|----------|
| Correctness against known values on a fixed graph | Yes |
| `nstart`, `personalization`, `dangling` on fixed graphs | Yes |
| Empty graph, multigraph, max_iter convergence failure | Yes |
| Google matrix eigenvector equivalence | Yes |
| **Property-based testing across varied graph structures** | **No** |

## Our 5 New Tests

All tests are in the `TestPageRankProperties` class using `pytest.mark.parametrize` across multiple graph structures.

### Test 1: `test_pagerank_valid_distribution_with_dangling`
**Property:** `sum(PR) == 1` and `PR(v) >= 0` for all nodes, even with dangling nodes (sinks).

Dangling nodes require special rank redistribution. A bug here silently breaks the probability distribution. NX only tests this on one fixed graph — we test across 6 different topologies including stars, chains, and disconnected components.

### Test 2: `test_pagerank_symmetric_graph_equal_ranks`
**Property:** In a complete directed graph, every node gets `PR = 1/n` for any alpha value.

Every node in a complete graph has identical in-degree and out-degree, so the stationary distribution must be uniform regardless of the damping factor. We test with 5 graph sizes × 4 alpha values = 20 cases. Not tested in NX.

### Test 3: `test_pagerank_alpha_zero_gives_uniform`
**Property:** When `α = 0`, every node gets `PR = 1/n` regardless of graph structure.

At α=0 the surfer never follows links — only teleports uniformly. The link structure becomes irrelevant. We test across complete, star, path, and cycle graphs. Not tested anywhere in NX.

### Test 4: `test_pagerank_adding_edges_increases_rank`
**Property (Monotonicity):** Adding incoming edges to a node never decreases its PageRank.

This is the core intuition of PageRank: more endorsements = higher importance. We compute PR before and after adding edges, and verify the target node's rank doesn't decrease. Not covered in NX.

### Test 5: `test_pagerank_personalization_boosts_target`
**Property:** Heavily biasing personalization towards a node increases its rank vs. uniform personalization.

Personalized PageRank is used in recommendation systems. NX tests personalization only with fixed expected values on one graph. We verify the relative property holds across different topologies.

## Summary Table

| # | Test Name | Property Verified | In NX? |
|---|-----------|-------------------|--------|
| 1 | `valid_distribution_with_dangling` | PR sums to 1, all >= 0 | Only 1 fixed graph |
| 2 | `symmetric_graph_equal_ranks` | PR = 1/n on complete graphs for any α | No |
| 3 | `alpha_zero_gives_uniform` | PR = 1/n when α = 0 | No |
| 4 | `adding_edges_increases_rank` | Monotonicity of incoming edges | No |
| 5 | `personalization_boosts_target` | Personalization raises target rank | Only fixed values |

## How to Run

```bash
# Run only the new property-based tests
pytest networkx/algorithms/link_analysis/tests/test_pagerank.py -v -k "TestPageRankProperties"

# Run all PageRank tests
pytest networkx/algorithms/link_analysis/tests/test_pagerank.py -v
```

## File Changed

- `networkx/algorithms/link_analysis/tests/test_pagerank.py` — added `TestPageRankProperties` class at the end of the file
