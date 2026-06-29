"""Functions for detecting communities based on the Infomap algorithm
(the map equation).
"""

from collections import Counter, defaultdict
from typing import NamedTuple

import networkx as nx
from networkx.algorithms.community.quality import _codelength, _flow, _plogp
from networkx.utils import py_random_state

__all__ = ["infomap_communities", "infomap_partitions"]


# ---------------------------------------------------------------------------
# The optimizer
#
# `quality.map_equation` says how good a partition is; this module searches for
# the partition that minimizes it. The search mirrors Louvain and adds
# Infomap's refinements, in four nested layers:
#
#   1. core loop      -- repeatedly move each node to the neighbouring module
#                        that most lowers the codelength (`_CoreOptimizer`),
#   2. aggregation    -- collapse the resulting modules into a super-network and
#                        run the core loop again, building modules of modules
#                        (`_find_top_modules`),
#   3. tuning         -- alternate fine-tuning (re-move single nodes) and
#                        coarse-tuning (re-split modules) to escape the local
#                        optima the greedy moves get stuck in (`_partition`),
#   4. hierarchy      -- stack super-modules on top and recurse into modules to
#                        recover a multilevel map (`_build_hierarchy`).
#
# `infomap_communities` runs this from several random starts and keeps the best.
#
# The move heuristics and loop structure follow the Infomap algorithm of Rosvall
# and Bergstrom, so the optimizer minimizes the same map equation and reaches the
# same optimum. The search is greedy and stochastic: a given seed fixes one path
# to a local optimum, and different seeds explore different ones.

# Tuning constants for the search: how many sweeps each loop runs before giving
# up, and how much a move (or a whole pass) must lower the codelength to count.
_CORE_LOOP_LIMIT = 10
_AGGREGATION_LOOP_LIMIT = 20
_MIN_IMPROVEMENT = 1e-10
_MIN_REL_TUNE_IMPROVEMENT = 1e-5
_MIN_SINGLE_NODE = 1e-16
_NUM_RANDOM_MOVES = 5
_MAX_DEGREE_FOR_RANDOM_MOVES = 2  # only low-degree nodes get random targets


def _module_codelength(enter, exit_, used):
    """One module's contribution to the two-level codelength: minus its enter
    and exit codebook terms, plus its module-usage term (``used = exit + visit
    rate``). The whole codelength sums this over every module and adds the index
    term ``_plogp(Q)`` and a constant node term (see
    :meth:`_CoreOptimizer.codelength`)."""
    return _plogp(used) - _plogp(enter) - _plogp(exit_)


class _MoveContext(NamedTuple):
    """The destination-independent part of a node's move delta: computed once
    per node by :meth:`_CoreOptimizer._prepare_move` and reused for every
    candidate module in :meth:`_CoreOptimizer._delta_codelength`."""

    node_enter: float
    node_exit: float
    node_flow: float
    old_cross: float  # flow the node shares with its current module
    enter_flow: float  # total inter-module (index) flow, Q
    p_enter_flow: float  # _plogp(enter_flow), cached to skip it per candidate
    old_delta: float  # change in the current module's codelength as the node leaves


class _CoreOptimizer:
    """Greedy single-node optimizer for the core loop.

    Maintains per-module flow data (flow, enter, exit) and the global codelength
    terms so each single-node move is evaluated and applied with an O(degree)
    delta, rather than recomputing the whole codelength each time. Self-link
    flow never crosses a module boundary, so it is excluded from enter/exit
    (kept in node flow).
    """

    def __init__(self, flow, links, module_of, seed, directed):
        """Set up the state needed for O(degree) moves on the partition
        `module_of`: per-node flow, per-module flow data, and the running
        codelength terms."""
        self.flow = flow
        self.seed = seed
        # Directedness comes from the graph, not from flow symmetry: a symmetric
        # directed graph (reciprocal equal-weight links) has symmetric flow yet
        # must still use the directed leftover-move rule below to match Infomap.
        self.directed = directed

        # Per node: its out-/in-link flows and their totals (its own exit/enter
        # rate). Self-links never cross a boundary, so drop them here.
        self.out = {u: {} for u in flow}
        self.in_ = {u: {} for u in flow}
        for u, v, f in links:
            if u == v:
                continue
            self.out[u][v] = self.out[u].get(v, 0.0) + f
            self.in_[v][u] = self.in_[v].get(u, 0.0) + f
        self.node_enter = {u: sum(self.in_[u].values()) for u in flow}
        self.node_exit = {u: sum(self.out[u].values()) for u in flow}
        self.node_log = sum(_plogp(flow[u]) for u in flow)  # constant node term

        # Per module: total flow, boundary-crossing enter/exit flow, and size.
        self.module_of = dict(module_of)
        self.module_flow = defaultdict(float)
        self.module_enter = defaultdict(float)
        self.module_exit = defaultdict(float)
        self.size = Counter()
        for u in flow:
            m = self.module_of[u]
            self.module_flow[m] += flow[u]
            self.size[m] += 1
            for v, f in self.out[u].items():
                if self.module_of[v] != m:
                    self.module_exit[m] += f
            for v, f in self.in_[u].items():
                if self.module_of[v] != m:
                    self.module_enter[m] += f

        # The codelength's running terms (see `codelength`), kept in sync by
        # `_apply` so the whole codelength is never recomputed from scratch.
        self.enter_flow = sum(self.module_enter.values())
        self.enter_log = sum(_plogp(v) for v in self.module_enter.values())
        self.exit_log = sum(_plogp(v) for v in self.module_exit.values())
        self.flow_log = sum(
            _plogp(self.module_exit[m] + self.module_flow[m]) for m in self.module_flow
        )

        # A pool of emptied module ids to reuse for "split into a new module".
        self._next_module = (max(self.module_of.values()) + 1) if self.module_of else 0
        self.empty = [m for m in list(self.size) if self.size[m] == 0]

    def codelength(self):
        """The current two-level codelength, the same quantity as
        :func:`~networkx.algorithms.community.quality.map_equation` but read off
        the running terms. ``index = plogp(Q) - enter_log``;
        ``module = -exit_log + flow_log - node_log``. The whole-network exit
        flow is 0, so it drops out of the index term."""
        return (
            _plogp(self.enter_flow)
            - self.enter_log
            - self.exit_log
            + self.flow_log
            - self.node_log
        )

    def _delta_flows(self, node):
        """``module -> [exit, enter]``: flow between `node` and each module it
        links to (out-links add to exit, in-links to enter)."""
        shared_flow = {}
        for v, f in self.out[node].items():
            entry = shared_flow.get(self.module_of[v])
            if entry is None:
                shared_flow[self.module_of[v]] = [f, 0.0]
            else:
                entry[0] += f
        for v, f in self.in_[node].items():
            entry = shared_flow.get(self.module_of[v])
            if entry is None:
                shared_flow[self.module_of[v]] = [0.0, f]
            else:
                entry[1] += f
        return shared_flow

    def _prepare_move(self, node, old, old_cross):
        """The part of a move's codelength delta that is fixed once `node` leaves
        its current module `old`. It does not depend on the destination, so
        compute it once here and reuse it for every candidate (see
        :meth:`_delta_codelength`). `old_cross` is the flow `node` shares with
        `old` (``exit + enter``).
        """
        node_enter = self.node_enter[node]
        node_exit = self.node_exit[node]
        node_flow = self.flow[node]
        enter = self.module_enter[old]
        exit_ = self.module_exit[old]
        used = exit_ + self.module_flow[old]
        # `old`'s codelength before and after `node` leaves it: it sheds the
        # node's enter/exit/flow, and the links they shared become crossing.
        old_before = _module_codelength(enter, exit_, used)
        old_after = _module_codelength(
            enter - node_enter + old_cross,
            exit_ - node_exit + old_cross,
            used - node_exit - node_flow + old_cross,
        )
        # `self.enter_flow` and the module terms are stable during the scan (no
        # move is applied until a winner is chosen), so capturing them is safe.
        return _MoveContext(
            node_enter,
            node_exit,
            node_flow,
            old_cross,
            self.enter_flow,
            _plogp(self.enter_flow),
            old_after - old_before,
        )

    def _delta_codelength(self, ctx, new, new_cross):
        """Change in total codelength if the node moves into module `new`.

        Moving a node touches only two modules' codebooks plus the shared index
        codebook, so the delta is the sum of three independent changes: the
        index term, `old`'s change (fixed for this node, precomputed in `ctx` by
        :meth:`_prepare_move`), and `new`'s change computed here. `new_cross` is
        the flow the node shares with `new` (``exit + enter``); joining `new`
        makes those links internal and brings the node's own flow with it.
        """
        enter = self.module_enter[new]
        exit_ = self.module_exit[new]
        used = exit_ + self.module_flow[new]
        new_before = _module_codelength(enter, exit_, used)
        new_after = _module_codelength(
            enter + ctx.node_enter - new_cross,
            exit_ + ctx.node_exit - new_cross,
            used + ctx.node_exit + ctx.node_flow - new_cross,
        )
        # Index codebook: only the total switching rate Q shifts. The node's
        # shared flow with `old` was internal and becomes crossing (+old_cross);
        # with `new` it was crossing and becomes internal (-new_cross); its flow
        # to all *other* modules stays crossing and cancels.
        q = ctx.enter_flow + ctx.old_cross - new_cross
        delta_index = _plogp(q) - ctx.p_enter_flow
        return delta_index + ctx.old_delta + (new_after - new_before)

    def _apply(self, node, new, shared_flow):
        """Move `node` into module `new`, updating the module flow data and the
        running codelength terms in place."""
        old = self.module_of[node]
        old_entry = shared_flow.get(old)
        old_cross = old_entry[0] + old_entry[1] if old_entry else 0.0
        new_entry = shared_flow.get(new)
        new_cross = new_entry[0] + new_entry[1] if new_entry else 0.0
        # 1. Remove the two modules' current contributions to the global terms.
        self.enter_flow -= self.module_enter[old] + self.module_enter[new]
        self.enter_log -= _plogp(self.module_enter[old]) + _plogp(
            self.module_enter[new]
        )
        self.exit_log -= _plogp(self.module_exit[old]) + _plogp(self.module_exit[new])
        self.flow_log -= _plogp(self.module_exit[old] + self.module_flow[old]) + _plogp(
            self.module_exit[new] + self.module_flow[new]
        )
        # 2. Carry the node's own flow from `old` to `new`.
        self.module_flow[old] -= self.flow[node]
        self.module_enter[old] -= self.node_enter[node]
        self.module_exit[old] -= self.node_exit[node]
        self.module_flow[new] += self.flow[node]
        self.module_enter[new] += self.node_enter[node]
        self.module_exit[new] += self.node_exit[node]
        # 3. Fix the boundary: links to `old` now cross it, links to `new` are
        #    now internal to it.
        self.module_enter[old] += old_cross
        self.module_exit[old] += old_cross
        self.module_enter[new] -= new_cross
        self.module_exit[new] -= new_cross
        # 4. Add the two modules' new contributions back.
        self.enter_flow += self.module_enter[old] + self.module_enter[new]
        self.enter_log += _plogp(self.module_enter[old]) + _plogp(
            self.module_enter[new]
        )
        self.exit_log += _plogp(self.module_exit[old]) + _plogp(self.module_exit[new])
        self.flow_log += _plogp(self.module_exit[old] + self.module_flow[old]) + _plogp(
            self.module_exit[new] + self.module_flow[new]
        )
        self.size[old] -= 1
        self.size[new] += 1
        self.module_of[node] = new

    def run(self, first_loop, loop_limit):
        """Sweep the nodes (in random order) up to `loop_limit` times, moving
        each to the module that lowers the codelength most, until a sweep stops
        improving the codelength. Returns the resulting codelength. On the initial
        all-singletons partition, `first_loop` lets nodes join modules but not
        leave them, so the first sweep builds modules up."""
        nodes = list(self.flow)
        old_codelength = self.codelength()
        for _ in range(loop_limit):
            num_moved = 0
            self.seed.shuffle(nodes)
            for node in nodes:
                current = self.module_of[node]
                # On the first sweep every node is alone; let nodes join modules but
                # not leave them, so the pass builds modules up instead of
                # reshuffling singletons.
                if first_loop and self.size[current] > 1:
                    continue

                # Candidate modules: the node's neighbours; for low-degree nodes, a
                # few random modules as well; and an empty module to split into. The
                # random and empty targets give the greedy search a way out of
                # shallow optima.
                shared_flow = self._delta_flows(node)
                candidates = set(shared_flow)
                if (
                    len(self.out[node]) + len(self.in_[node])
                    <= _MAX_DEGREE_FOR_RANDOM_MOVES
                ):
                    for _ in range(_NUM_RANDOM_MOVES):
                        candidates.add(self.module_of[self.seed.choice(nodes)])
                candidates.discard(current)
                empty_module = None
                if self.size[current] > 1:
                    empty_module = self.empty[-1] if self.empty else self._next_module
                    candidates.add(empty_module)
                if not candidates:
                    continue

                old_entry = shared_flow.get(current)
                old_cross = old_entry[0] + old_entry[1] if old_entry else 0.0
                ctx = self._prepare_move(node, current, old_cross)
                best_module, best_delta = current, 0.0
                # Track which candidate the node sends the most flow to; ties in
                # codelength are broken toward it (see below). Seed it with the
                # current module so a move wins the tie only by being more cohesive.
                strong_module = current
                strong_exit = old_entry[0] if old_entry else 0.0
                strong_delta = 0.0
                for module in candidates:
                    entry = shared_flow.get(module)
                    new_cross = entry[0] + entry[1] if entry else 0.0
                    delta = self._delta_codelength(ctx, module, new_cross)
                    if delta < best_delta - _MIN_SINGLE_NODE:
                        best_delta, best_module = delta, module
                    exit_to = entry[0] if entry else 0.0
                    if exit_to > strong_exit:
                        strong_exit, strong_module, strong_delta = (
                            exit_to,
                            module,
                            delta,
                        )
                # Tie-break: when a move barely changes the codelength (within
                # _MIN_SINGLE_NODE of the best, even slightly worse), prefer the
                # module the node sends the most exit flow to. It is free now and
                # usually compresses better on later sweeps.
                if (
                    strong_module != best_module
                    and strong_delta <= best_delta + _MIN_SINGLE_NODE
                ):
                    best_module = strong_module
                if best_module == current:
                    continue

                if best_module == empty_module:
                    if self.empty:
                        self.empty.pop()
                    else:
                        self._next_module += 1
                # Neighbours of `node` still in `current`, taken before the move
                # since `_apply` rewrites `module_of`. Used below to rescue a node
                # the move would otherwise leave stranded.
                linked_in_old = [
                    w
                    for w in set(self.out[node]) | set(self.in_[node])
                    if self.module_of[w] == current
                ]
                self._apply(node, best_module, shared_flow)
                num_moved += 1
                if self.size[current] == 0:
                    self.empty.append(current)
                elif self.size[current] == 1 and len(linked_in_old) == 1:
                    leftover = linked_in_old[0]
                    # A leftover linked to the mover by a single link is about to
                    # sit alone with no internal flow, costing index codebook for
                    # nothing, so move it along too. A directed reciprocal pair (a
                    # link each way) keeps flow between the two, so leave it.
                    n_links = (
                        (leftover in self.out[node]) + (leftover in self.in_[node])
                        if self.directed
                        else 1
                    )
                    if n_links == 1:
                        self._apply(leftover, best_module, self._delta_flows(leftover))
                        num_moved += 1
                        if self.size[current] == 0:
                            self.empty.append(current)
            # Stop once a whole sweep no longer lowers the codelength enough.
            # Besides saving sweeps, this bounds the neutral lateral moves the
            # strongest-connected tie-break can otherwise keep making.
            new_codelength = self.codelength()
            if num_moved == 0 or new_codelength >= old_codelength - _MIN_IMPROVEMENT:
                break
            old_codelength = new_codelength
        return self.codelength()


def _core_loop(
    flow, links, module_of, seed, directed, first_loop=False, loop_limit=None
):
    """Run the stateful core optimizer on `module_of` (mutated in place) and
    return the resulting codelength."""
    optimizer = _CoreOptimizer(flow, links, module_of, seed, directed)
    codelength = optimizer.run(
        first_loop, _CORE_LOOP_LIMIT if loop_limit is None else loop_limit
    )
    module_of.clear()
    module_of.update(optimizer.module_of)
    return codelength


def _collapse(flow, links, module_of):
    """Aggregate modules into super-nodes, preserving the map equation.

    Returns ``(super_flow, super_links, relabel)`` where ``relabel`` maps each
    original module id to its super-node id (``0..k-1``). A super-node's flow is
    the total flow of its module; super-links carry the summed inter-module
    flow. Intra-module flow never crosses a boundary, so self-loops are dropped.
    """
    relabel = {m: i for i, m in enumerate(sorted(set(module_of.values())))}
    super_flow = defaultdict(float)
    for node, f in flow.items():
        super_flow[relabel[module_of[node]]] += f
    super_links = defaultdict(float)
    for u, v, f in links:
        a, b = relabel[module_of[u]], relabel[module_of[v]]
        if a != b:
            super_links[a, b] += f
    links_list = [(a, b, f) for (a, b), f in super_links.items()]
    return dict(super_flow), links_list, relabel


def _induced(flow, links, nodes):
    """Restrict the flow network to `nodes`: their visit rates and the links
    with both endpoints inside (the induced sub-network)."""
    nodeset = set(nodes)
    sub_flow = {node: flow[node] for node in nodes}
    sub_links = [(u, v, f) for u, v, f in links if u in nodeset and v in nodeset]
    return sub_flow, sub_links


def _find_top_modules(flow, links, module_of, seed, directed, first_loop=False):
    """Aggregation phase: starting from the current partition, repeatedly
    collapse modules into a super-network and run the core loop on it, accepting
    each level only while it lowers the codelength.
    Returns a (possibly coarser) base-level ``node -> module`` mapping.

    `first_loop` marks the very first partition of the full network, where the
    core loop forbids pulling a node out of a multi-member module; it only
    applies to the finest (level-0) aggregation pass.
    """
    module_of = dict(module_of)
    codelength = _codelength(flow, links, module_of)
    level = 0
    while len(set(module_of.values())) > 1:
        super_flow, super_links, relabel = _collapse(flow, links, module_of)
        super_module = {node: i for i, node in enumerate(super_flow)}
        _core_loop(
            super_flow,
            super_links,
            super_module,
            seed,
            directed,
            first_loop=(first_loop and level == 0),
            loop_limit=_CORE_LOOP_LIMIT if level == 0 else _AGGREGATION_LOOP_LIMIT,
        )
        if len(set(super_module.values())) == len(super_flow):
            break  # core loop merged nothing -> converged
        candidate = {node: super_module[relabel[module_of[node]]] for node in flow}
        new_codelength = _codelength(flow, links, candidate)
        if new_codelength > codelength - _MIN_IMPROVEMENT:
            break
        module_of, codelength = candidate, new_codelength
        level += 1
    return module_of


def _coarse_tune(flow, links, module_of, seed, directed):
    """Coarse-tune: split each module into sub-modules by
    optimizing the induced sub-network, then let those sub-modules regroup
    starting from the current modular structure. Returns a ``node -> module``
    mapping (the caller decides whether it improved)."""
    members = defaultdict(list)
    for node, module in module_of.items():
        members[module].append(node)

    submodule_of = {}
    offset = 0
    for nodes in members.values():
        if len(nodes) < 2:
            for node in nodes:
                submodule_of[node] = offset
            offset += 1
            continue
        sub_flow, sub_links = _induced(flow, links, nodes)
        singletons = {node: i for i, node in enumerate(sub_flow)}
        sub_partition = _find_top_modules(
            sub_flow, sub_links, singletons, seed, directed
        )
        relabel = {
            s: offset + i for i, s in enumerate(sorted(set(sub_partition.values())))
        }
        for node in nodes:
            submodule_of[node] = relabel[sub_partition[node]]
        offset += len(relabel)

    # Aggregate the sub-modules, seed each in its original module, and let them
    # regroup with one core-loop run; expanding the result is the tuned partition.
    super_flow, super_links, relabel = _collapse(flow, links, submodule_of)
    super_origin = {relabel[submodule_of[node]]: module_of[node] for node in flow}
    super_module = dict(super_origin)
    _core_loop(super_flow, super_links, super_module, seed, directed)
    return {node: super_module[relabel[submodule_of[node]]] for node in flow}


def _fine_tune(flow, links, module_of, seed, directed):
    """Fine-tune: re-run the core loop on individual nodes,
    starting from the current modular structure. Returns a ``node -> module``
    mapping."""
    module_of = dict(module_of)
    _core_loop(flow, links, module_of, seed, directed)
    return module_of


def _partition(flow, links, seed, directed, first_loop=True):
    """The two-level partition: an initial aggregation followed by an
    alternating fine-tune / coarse-tune loop, re-aggregating after each tune,
    until neither improves the codelength (and coarse-tune has been tried).

    `first_loop` forbids pulling a node out of a multi-member module on the very
    first sweep; it holds only for the main network. Recursive partitions of
    super- and sub-networks (the index level and refinement) pass False, matching
    the reference, where this guard is gated on the main Infomap at level 0."""
    one_level = _codelength(flow, links, dict.fromkeys(flow, 0))

    module_of = _find_top_modules(
        flow,
        links,
        {n: i for i, n in enumerate(flow)},
        seed,
        directed,
        first_loop=first_loop,
    )
    old_codelength = _codelength(flow, links, module_of)

    do_fine_tune = True
    coarse_tuned = False
    while len(set(module_of.values())) > 1:
        if do_fine_tune:
            tuned = _fine_tune(flow, links, module_of, seed, directed)
        else:
            coarse_tuned = True
            tuned = _coarse_tune(flow, links, module_of, seed, directed)
        if _codelength(flow, links, tuned) < _codelength(flow, links, module_of):
            module_of = _find_top_modules(flow, links, tuned, seed, directed)

        new_codelength = _codelength(flow, links, module_of)
        is_improvement = (
            new_codelength <= old_codelength - _MIN_IMPROVEMENT
            and new_codelength < old_codelength - one_level * _MIN_REL_TUNE_IMPROVEMENT
        )
        if not is_improvement:
            if coarse_tuned:
                break
        else:
            old_codelength = new_codelength
        do_fine_tune = not do_fine_tune

    # Never do worse than putting everything in one module.
    if _codelength(flow, links, module_of) > one_level:
        return dict.fromkeys(flow, 0)
    return module_of


def _find_super_modules(flow, links, group_of, seed, directed):
    """Coarsen the current top-level groups into super-groups. The index-level
    super-network uses each module's *enter flow* as its node flow, not its
    visit rate. Returns ``group_id -> super_id`` or None if trivial."""
    modules = sorted(set(group_of.values()))
    if len(modules) <= 2:
        return None
    relabel = {m: i for i, m in enumerate(modules)}
    enter = defaultdict(float)
    super_links = defaultdict(float)
    for u, v, f in links:
        a, b = group_of[u], group_of[v]
        if a != b:
            enter[relabel[b]] += f
            super_links[relabel[a], relabel[b]] += f
    super_flow = {i: enter.get(i, 0.0) for i in range(len(modules))}
    super_links = [(a, b, f) for (a, b), f in super_links.items()]
    super_partition = _partition(
        super_flow, super_links, seed, directed, first_loop=False
    )
    n_super = len(set(super_partition.values()))
    if n_super == 1 or n_super == len(modules):
        return None
    return {m: super_partition[relabel[m]] for m in modules}


def _refine_hierarchy(flow, links, path, seed, directed):
    """Recursively split each innermost module into sub-modules, appending a
    deeper level whenever it lowers the hierarchical codelength."""
    groups = defaultdict(list)
    for node, p in path.items():
        groups[p].append(node)
    changed = False
    new_path = dict(path)
    for p, nodes in groups.items():
        if len(nodes) <= 2:
            continue
        sub_flow, sub_links = _induced(flow, links, nodes)
        sub = _partition(sub_flow, sub_links, seed, directed, first_loop=False)
        k = len(set(sub.values()))
        if k == 1 or k == len(nodes):
            continue
        candidate = dict(new_path)
        for n in nodes:
            candidate[n] = p + (sub[n],)
        if (
            _hierarchical_codelength(flow, links, candidate)
            < _hierarchical_codelength(flow, links, new_path) - _MIN_IMPROVEMENT
        ):
            new_path = candidate
            changed = True
    if changed:
        new_path = _refine_hierarchy(flow, links, new_path, seed, directed)
    return new_path


def _build_hierarchy(flow, links, seed, directed):
    """Build a multilevel partition: two-level modules, coarsened by super-
    levels above and refined by sub-levels below, accepting each change only
    when it lowers the hierarchical codelength. Returns ``node -> path tuple``
    (top level first)."""
    top = _partition(flow, links, seed, directed)
    path = {node: (top[node],) for node in flow}
    while True:  # coarsen: prepend super-levels
        coarsest = {node: path[node][0] for node in flow}
        super_of = _find_super_modules(flow, links, coarsest, seed, directed)
        if super_of is None:
            break
        candidate = {node: (super_of[coarsest[node]],) + path[node] for node in flow}
        if (
            _hierarchical_codelength(flow, links, candidate)
            < _hierarchical_codelength(flow, links, path) - _MIN_IMPROVEMENT
        ):
            path = candidate
        else:
            break
    return _refine_hierarchy(
        flow, links, path, seed, directed
    )  # refine: append sub-levels


def _hierarchical_codelength(flow, links, path):
    """Multilevel map equation codelength of a hierarchical partition.

    ``path[node]`` is the tuple of module ids from the top level down to the
    node's innermost module. This is the recursive generalization of the
    two-level codelength: every module pays ``plogp(exit + sum child_enter) -
    plogp(exit) - sum plogp(child_enter)`` where a leaf child contributes its
    node visit rate.
    """
    # Each module in the tree is identified by a path prefix; record the tree
    # structure (a module's child sub-modules and its directly-held leaf nodes).
    prefixes = set()
    for p in path.values():
        for k in range(1, len(p) + 1):
            prefixes.add(p[:k])
    children = defaultdict(set)
    for q in prefixes:
        if len(q) > 1:
            children[q[:-1]].add(q)
    leaf_nodes = defaultdict(list)
    for node, p in path.items():
        leaf_nodes[p].append(node)

    # A link u->v crosses the boundary of every module that contains exactly one
    # of its endpoints: those strictly below the level where the two paths first
    # differ. It exits each such module on u's side and enters each on v's side.
    enter = defaultdict(float)
    exit_ = defaultdict(float)
    for u, v, f in links:
        pu, pv = path[u], path[v]
        common = 0
        for a, b in zip(pu, pv):
            if a != b:
                break
            common += 1
        for k in range(common + 1, len(pu) + 1):
            exit_[pu[:k]] += f
        for k in range(common + 1, len(pv) + 1):
            enter[pv[:k]] += f

    # Root index codebook: encodes which top module the walk enters.
    root_children = [q for q in prefixes if len(q) == 1]
    total = _plogp(sum(enter[q] for q in root_children)) - sum(
        _plogp(enter[q]) for q in root_children
    )
    # Every module pays its own codebook: it codes entering each child (a
    # sub-module's enter flow, or a leaf node's visit rate) and exiting itself.
    for p in prefixes:
        child_enter = [enter[c] for c in children.get(p, ())]
        child_enter += [flow[node] for node in leaf_nodes.get(p, ())]
        total += (
            _plogp(exit_[p] + sum(child_enter))
            - _plogp(exit_[p])
            - sum(_plogp(c) for c in child_enter)
        )
    return total


def _check_num_trials(num_trials):
    """Validate the ``num_trials`` argument shared by the public functions."""
    if not isinstance(num_trials, int) or num_trials < 1:
        raise ValueError("num_trials must be a positive integer")


@py_random_state("seed")
@nx._dispatchable(edge_attrs="weight")
def infomap_communities(G, *, weight="weight", seed=None, num_trials=1):
    r"""Find communities in `G` using the Infomap algorithm (the map equation).

    Infomap detects community structure by minimizing the *map equation* [1]_,
    the expected per-step description length of a random walk on the network.
    Unlike the modularity-based methods :any:`louvain_communities` and
    :any:`leiden_communities`, Infomap is a *flow-based* method, which makes it
    a natural fit for networks where community structure is carried by the
    direction and volume of flow.

    For a two-level partition :math:`\mathsf{M}` the map equation is

    .. math::
        L(\mathsf{M}) = q_\curvearrowleft H(\mathcal{Q})
            + \sum_{i} p^i_\circlearrowright H(\mathcal{P}^i)

    where the first term is the cost of coding transitions *between* modules
    (the index codebook, used at the total exit rate :math:`q_\curvearrowleft`)
    and the second is the cost of coding visits *within* each module :math:`i`.
    Lower codelength means a partition that compresses the flow better.

    The optimizer follows the same two phases as Louvain -- greedily moving
    single nodes to neighbouring modules, then aggregating modules into a
    super-network and repeating -- and adds Infomap's fine-tuning and
    coarse-tuning passes. It returns the two-level partition that minimizes the
    map equation; for the multilevel (hierarchical) partition [2]_, see
    :func:`infomap_partitions`. The search is stochastic, so `num_trials`
    independent restarts are run and the lowest-codelength partition is kept.

    Edge weights are interpreted as flow. For directed graphs the visit rates
    are the stationary distribution of a random walk with teleportation, as in
    PageRank.

    Parameters
    ----------
    G : NetworkX graph
        An undirected or directed graph; multigraphs are accepted and parallel
        edges are summed. Edge weights are interpreted as flow and must be
        finite and non-negative.
    weight : string or None, optional (default="weight")
        The name of an edge attribute holding the numerical weight. If None,
        every edge has weight 1.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    num_trials : int, optional (default=1)
        Number of independent restarts; the partition with the lowest
        codelength is returned.

    Returns
    -------
    list of sets of nodes
        A partition of `G` as a list of disjoint sets of nodes, together
        containing every node. This is the two-level partition that minimizes
        the map equation.

    Raises
    ------
    ValueError
        If `num_trials` is not a positive integer, or if any edge weight is
        negative or not finite.

    Notes
    -----
    The search is stochastic: `seed` fixes the random move order (so a given
    seed is reproducible), and `num_trials` restarts improve the chance of
    reaching the global optimum.

    Self-loops add only to a node's within-module flow; they never cross a
    module boundary, so they do not affect where a node moves.

    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> communities = nx.community.infomap_communities(G, seed=0)
    >>> nx.community.is_partition(G, communities)
    True

    References
    ----------
    .. [1] Rosvall, M. & Bergstrom, C.T. Maps of random walks on complex
       networks reveal community structure. PNAS 105, 1118-1123 (2008).
       https://doi.org/10.1073/pnas.0706851105
    .. [2] Rosvall, M. & Bergstrom, C.T. Multilevel compression of random walks
       on networks reveals hierarchical organization in large integrated
       systems. PLoS ONE 6(4), e18209 (2011).
       https://doi.org/10.1371/journal.pone.0018209

    See Also
    --------
    infomap_partitions
    :func:`~networkx.algorithms.community.quality.map_equation`
    :any:`louvain_communities`
    :any:`leiden_communities`
    """
    _check_num_trials(num_trials)
    # The flow depends only on the graph, so compute it once and reuse it across
    # every restart and codelength evaluation.
    visit_rate, link_flows = _flow(G, weight)
    flow = dict(visit_rate)
    if not flow:
        return []  # empty graph
    module_of = _best_two_level(flow, link_flows, seed, num_trials, G.is_directed())
    groups = {}
    for node, module in module_of.items():
        groups.setdefault(module, set()).add(node)
    return list(groups.values())


def _best_two_level(flow, links, seed, num_trials, directed):
    """Return the lowest-codelength two-level partition over `num_trials`
    restarts, as a ``node -> module`` mapping."""
    best_module_of, best_codelength = None, float("inf")
    for _ in range(num_trials):
        module_of = _partition(flow, links, seed, directed)
        codelength = _codelength(flow, links, module_of)
        if codelength < best_codelength:
            best_codelength, best_module_of = codelength, module_of
    return best_module_of


def _best_hierarchy(flow, links, seed, num_trials, directed):
    """Return the lowest-codelength multilevel partition over `num_trials`
    restarts, as a ``node -> path`` mapping (top module first)."""
    best_path, best_codelength = None, float("inf")
    for _ in range(num_trials):
        path = _build_hierarchy(flow, links, seed, directed)
        codelength = _hierarchical_codelength(flow, links, path)
        if codelength < best_codelength:
            best_codelength, best_path = codelength, path
    return best_path


@py_random_state("seed")
@nx._dispatchable(edge_attrs="weight")
def infomap_partitions(G, *, weight="weight", seed=None, num_trials=1):
    r"""Yield the community partition at each level of the Infomap hierarchy.

    Infomap finds a multilevel (hierarchical) partition by minimizing the map
    equation (see :func:`infomap_communities`). This generator yields one flat
    partition per level of that hierarchy, from the coarsest (the top-level
    modules) to the finest. Each yielded value is a list of disjoint sets of
    nodes that together contain every node of `G`.

    Parameters
    ----------
    G : NetworkX graph
        An undirected or directed graph; multigraphs are accepted and parallel
        edges are summed. Edge weights are interpreted as flow and must be
        finite and non-negative.
    weight : string or None, optional (default="weight")
        The name of an edge attribute holding the numerical weight. If None,
        every edge has weight 1.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    num_trials : int, optional (default=1)
        Number of independent restarts; the levels of the lowest-codelength
        hierarchy found are yielded. Must be a positive integer.

    Yields
    ------
    list of sets of nodes
        The partition of `G` at the current hierarchy level, coarsest first.

    Raises
    ------
    ValueError
        If `num_trials` is not a positive integer, or if any edge weight is
        negative or not finite.

    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> levels = list(nx.community.infomap_partitions(G, seed=0))
    >>> all(nx.community.is_partition(G, p) for p in levels)
    True

    See Also
    --------
    infomap_communities
    :func:`~networkx.algorithms.community.quality.map_equation`
    :any:`louvain_partitions`
    """
    _check_num_trials(num_trials)
    # Validate num_trials eagerly so a bad value raises on call, not mid-iteration.
    # The hierarchy search runs here; only splitting the result into per-level
    # partitions is deferred to the `_expand_levels` generator.
    visit_rate, link_flows = _flow(G, weight)
    flow = dict(visit_rate)
    if not flow:
        return iter([[]])  # empty graph -> one empty level (matches louvain_partitions)
    path = _best_hierarchy(flow, link_flows, seed, num_trials, G.is_directed())
    return _expand_levels(path)


def _expand_levels(path):
    """Yield the partition at each hierarchy level of a ``node -> path`` mapping,
    coarsest level first; each is a list of node sets covering all of `G`."""
    depth = max(len(p) for p in path.values())
    for level in range(1, depth + 1):
        groups = {}
        for node, node_path in path.items():
            groups.setdefault(node_path[:level], set()).add(node)
        yield list(groups.values())
