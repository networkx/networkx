"""
Minimal fractional maximum matching with fewest ½‑edges,
refactored for clarity, safety and re‑use.

Implements the Bourjolly–Pulleyblank algorithm.

Author: Roi Sibony (refactor by ChatGPT)
Date: 2025‑06‑08
"""
from __future__ import annotations

import logging
from collections import defaultdict, deque
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
from networkx.utils import not_implemented_for

log = logging.getLogger(__name__)  # library code should not force logging setup


class Label(Enum):
    """Vertex search labels used by the algorithm."""

    PLUS = auto()
    MINUS = auto()


# ---------------------------------------------------------------------------
# Symmetric edge helpers
# ---------------------------------------------------------------------------

def _get_val(x: Dict[Tuple[Any, Any], float], u: Any, v: Any) -> float:
    """Return x[(u,v)] (or 0 if absent) ensuring symmetry is transparent."""
    return x.get((u, v), 0.0)


def _set_val(x: Dict[Tuple[Any, Any], float], u: Any, v: Any, val: float) -> None:
    """Store *both* directions of edge (u,v) with the same value."""
    x[(u, v)] = val
    x[(v, u)] = val


# ---------------------------------------------------------------------------
# Public wrapper
# ---------------------------------------------------------------------------

@not_implemented_for("multigraph")
@not_implemented_for("directed")
def minimal_fraction_max_matching(
    G: nx.Graph, *, initial_matching: Optional[Dict[Tuple[Any, Any], float]] = None
) -> Dict[Tuple[Any, Any], float]:
    """Return a maximum fractional matching using the fewest ½‑edges.

    Parameters
    ----------
    G : nx.Graph
        Undirected *simple* graph.
    initial_matching : dict[(u,v),float] | None, optional
        Pre‑seed the matching (values in {0,½,1}).

    Notes
    -----
    Implementation follows: *König–Egerváry graphs, 2‑bicritical graphs and
    fractional matchings* (Bourjolly & Pulleyblank, 1984).
    """
    solver = _FractionalMatchingSolver(G, initial_matching or {})
    log.debug("%s Starting solver", "#" * 20)
    return solver.solve()


# ---------------------------------------------------------------------------
# Solver class (internal)
# ---------------------------------------------------------------------------


class _FractionalMatchingSolver:
    """Internal class running the augmentation procedure."""

    def __init__(self, G: nx.Graph, initial: Dict[Tuple[Any, Any], float]):  # noqa: D401
        self.G = G
        self.x: Dict[Tuple[Any, Any], float] = {}
        for (u, v), val in initial.items():
            _set_val(self.x, u, v, val)

        # search state (re‑initialised each phase)
        self.labels: Dict[Any, Optional[Label]] = {}
        self.preds: Dict[Any, Optional[Any]] = {}

    # ------------------------ public driver -------------------------------
    def solve(self) -> Dict[Tuple[Any, Any], float]:
        """Run repeated augmentation phases until maximal."""
        while True:
            self._initialise_phase()

            augmented_this_phase = False
            frontier = deque(v for v, lab in self.labels.items() if lab is Label.PLUS)

            while frontier:
                u = frontier.popleft()
                res = self._scan_edges_from(u)
                if res is None:
                    continue
                src, dst = res

                if self.labels.get(dst) is Label.PLUS:
                    self._augment(src, dst)
                    augmented_this_phase = True
                    break

                # dst unlabeled
                if self._label_or_augment(src, dst):
                    self._augment(src, dst)
                    augmented_this_phase = True
                    break
                else:
                    # new '+' labels may have been added
                    frontier.extend(
                        w
                        for w, lab in self.labels.items()
                        if lab is Label.PLUS and w not in frontier
                    )

            if not augmented_this_phase:
                break  # optimal

        # return canonical direction only
        return {(u, v): val for (u, v), val in self.x.items() if u < v and val > 0}

    # ------------------------ phase helpers ------------------------------
    def _initialise_phase(self) -> None:
        """Label unsaturated vertices PLUS; others unlabeled (None)."""
        self.labels.clear()
        self.preds = {v: None for v in self.G.nodes}

        saturation = defaultdict(float)
        for (u, _), val in self.x.items():
            saturation[u] += val

        for v in self.G.nodes:
            self.labels[v] = Label.PLUS if saturation[v] < 1 else None

    # ------------------------------------------------------------------
    def _scan_edges_from(self, u: Any) -> Optional[Tuple[Any, Any]]:
        """Return a candidate edge (u,v) to process or None."""
        for v in self.G.neighbors(u):
            lab_v = self.labels.get(v)
            edge_val = _get_val(self.x, u, v)

            if lab_v is Label.MINUS:
                continue
            if lab_v is Label.PLUS:
                return u, v
            # unlabeled
            if edge_val < 1:
                return u, v
        return None

    # ------------------------------------------------------------------
    def _trace_to_root(self, start: Any) -> List[Any]:
        """Return path from *start* to its root via predecessors (inclusive)."""
        path = [start]
        curr = start
        while self.preds[curr] is not None:
            curr = self.preds[curr]
            path.append(curr)
        return path

    # ------------------------------------------------------------------
    def _augment(self, u: Any, v: Any) -> None:
        """Perform type 1 or type 3 augmentation through (u,v)."""
        path_u = self._trace_to_root(u)
        path_v = self._trace_to_root(v)

        if path_u[-1] != path_v[-1]:  # type 1
            path_u.reverse()
            self._flip_path_edges(path_u)
            _set_val(self.x, u, v, 1 - _get_val(self.x, u, v))
            self._flip_path_edges(path_v)

        else:  # type 3 (cycle)
            cycle = self._build_cycle(path_u, path_v)
            if not cycle:
                raise RuntimeError("Unexpected empty cycle in type 3 augmentation")
            self._flip_cycle_half_edges(cycle)
            # finish by toggling path_v (to give 1s on alternate edges)
            path_v.reverse()
            self._flip_path_edges(path_v)

        # clear labels for next phase
        self.labels.clear()
        self.preds.clear()

    # ------------------------ flip helpers ------------------------------
    def _flip_path_edges(self, path: List[Any]) -> None:
        for a, b in zip(path, path[1:]):
            _set_val(self.x, a, b, 1 - _get_val(self.x, a, b))

    def _flip_cycle_half_edges(self, cycle: List[Any]) -> None:
        for i, (a, b) in enumerate(zip(cycle, cycle[1:] + [cycle[0]])):
            new_val = 0.5 if _get_val(self.x, a, b) != 0.5 else 0.0
            _set_val(self.x, a, b, new_val)

    # ------------------------------------------------------------------
    @staticmethod
    def _build_cycle(path_u: List[Any], path_v: List[Any]) -> List[Any]:
        """Return ordered vertices of u … v cycle (simple)."""
        set_u = set(path_u)
        lca = next(node for node in path_v if node in set_u)
        idx_u = path_u.index(lca)
        idx_v = path_v.index(lca)
        return path_u[: idx_u + 1] + list(reversed(path_v[:idx_v]))

    # ------------------------------------------------------------------
    def _label_or_augment(self, u: Any, v: Any) -> bool:
        """Try to extend labels via *v* or do type 2 augmentation.

        Returns
        -------
        bool
            True  -> performed type 2 augmentation (caller must augment)
            False -> merely extended labels, continue scanning
        """
        # look for neighbour with x=1
        for w in self.G.neighbors(v):
            if _get_val(self.x, v, w) == 1:
                self.labels[v] = Label.MINUS
                self.labels[w] = Label.PLUS
                self.preds[v] = u
                self.preds[w] = v
                return False

        # type 2 augmentation on ½‑cycle through v
        cycle = self._find_half_cycle(v)
        self._augment_type2_cycle(cycle)
        return True

    # ------------------------------------------------------------------
    def _find_half_cycle(self, start: Any) -> List[Any]:
        """Return a ½‑edge cycle starting at *start* (guaranteed by theory)."""
        cycle = [start]
        visited = {start}

        while True:
            current = cycle[-1]
            for nxt in self.G.neighbors(current):
                if _get_val(self.x, current, nxt) == 0.5:
                    if nxt == start and len(cycle) > 1:
                        return cycle
                    if nxt not in visited:
                        cycle.append(nxt)
                        visited.add(nxt)
                        break
            else:
                raise RuntimeError("Failed to find ½‑cycle in type 2 augmentation")

    def _augment_type2_cycle(self, cycle: List[Any]) -> None:
        """Flip ½‑edges of *cycle* to alternating 0/1 pattern (type 2)."""
        for i, (a, b) in enumerate(zip(cycle, cycle[1:] + [cycle[0]])):
            new_val = 0.0 if i % 2 == 0 else 1.0
            _set_val(self.x, a, b, new_val)
        # after augmentation, labels/preds will be cleared by caller

# ---------------------------------------------------------------------------
# Demonstration (quick sanity‑check)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import random

    random.seed(0)
    demo_G = nx.Graph([(1, 2), (1, 3), (2, 3), (3, 4)])
    print("fractional matching =>", minimal_fraction_max_matching(demo_G))
