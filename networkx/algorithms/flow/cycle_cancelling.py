import math
from copy import deepcopy

import networkx as nx
from networkx.exception import NetworkXError, NetworkXUnbounded


def cycle_cancelling(
    G,
    s,
    t,
    weight="weight",
    flow_func=None,
    capacity="capacity",
    negative_cycle_func=None,
):
    """
    Cycle-Cancelling algorithm for Minimum-Cost Flow.

    Parameters:
        G : directed graph (DiGraph)
        s : source node
        t : target node
        weight : edge attribute for cost
        capacity : edge attribute for capacity
        flow_func : flow function to use in finding the maximum flow
        negative_cycle_func : function to fins the negative cycles


    Returns:
        (flow_dict, min_cost)
    """

    # --------------------------------------------------------
    # 1. PARAMETER VALIDATION
    # --------------------------------------------------------

    if not isinstance(G, nx.DiGraph):
        raise TypeError("Input graph must be a directed graph (DiGraph).")

    if s not in G.nodes:
        raise ValueError("Source node does not exist in graph.")

    if t not in G.nodes:
        raise ValueError("Target node does not exist in graph.")

    for u, v, data in G.edges(data=True):
        if capacity not in data:
            raise ValueError(f"Edge ({u},{v}) missing capacity attribute.")
        if data[capacity] < 0:
            raise ValueError(f"Edge ({u},{v}) has negative capacity.")

        if weight not in data:
            raise ValueError(f"Edge ({u},{v}) missing weight attribute.")
        # the algorithm can run on negative too - think of delete it
        if data[weight] < 0:
            raise ValueError(f"Edge ({u},{v}) has negative weight ({data[weight]}).")

    if negative_cycle_func is None:
        from networkx.algorithms.cycles.karp import karp

        negative_cycle_func = karp

    if not callable(negative_cycle_func):
        raise nx.NetworkXError("finding negative cycle func has to be callable.")

    # --------------------------------------------------------
    # 2. INITIAL MAX-FLOW (IGNORE COSTS)
    # --------------------------------------------------------

    # We temporarily build a capacity-only graph
    G_cap = nx.DiGraph()
    for u, v, data in G.edges(data=True):
        G_cap.add_edge(u, v, capacity=data[capacity])

    max_flow_return = nx.maximum_flow(
        G_cap, s, t, flow_func=None
    )  # flow_dict is a nested dict
    flow_dict = max_flow_return[1]

    for u, v in G_cap.edges():
        # If node u has no outgoing flow dict, create one
        if u not in flow_dict:
            flow_dict[u] = {}

        # If edge (u, v) not assigned by max-flow, its flow is 0
        if v not in flow_dict[u]:
            flow_dict[u][v] = 0

    # --------------------------------------------------------
    # 3. BUILD INITIAL RESIDUAL GRAPH
    # --------------------------------------------------------

    def build_residual(G, flow):
        # We use MultiDiGraph because u->v might have a forward residual edge
        # AND a backward residual edge from the opposite original edge v->u.
        R = nx.DiGraph()
        for u, v, data in G.edges(data=True):
            cap = data[capacity]
            w = data[weight]
            f = flow.get(u, {}).get(v, 0)

            # Forward residual edge: can push (cap - f) more flow at cost 'w'
            # for negative cycle, we need only the bwd edge, otherwise we work with an edge without flow
            if f < cap:
                if R.has_edge(u, v):
                    if R[u][v]["type"] == "bwd":
                        continue
                else:
                    R.add_edge(u, v, weight=w, capacity=cap - f, type="fwd")

            # Backward residual edge: can push 'f' back at cost '-w'
            if f > 0:
                if R.has_edge(v, u):
                    if R[v][u]["type"] == "fwd":
                        R.remove_edge(v, u)
                R.add_edge(v, u, weight=-w, capacity=f, type="bwd")

        return R

    # --------------------------------------------------------
    # Helper: increase flow on edges of a cycle
    # --------------------------------------------------------

    def augment_cycle(flow, cycle, bottleneck):
        """Increase flow along cycle edges by bottleneck."""
        for i in range(len(cycle) - 1):
            u = cycle[i]
            v = cycle[i + 1]

            if G.has_edge(u, v) and R.has_edge(u, v) and R[u][v]["type"] == "fwd":
                # forward edge (u→v)
                flow.setdefault(u, {}).setdefault(v, 0)
                flow[u][v] += bottleneck

            elif G.has_edge(v, u) and R.has_edge(u, v) and R[u][v]["type"] == "bwd":
                # backward edge (v→u)
                flow.setdefault(v, {}).setdefault(u, 0)
                flow[v][u] -= bottleneck  # reduce forward flow

            else:
                raise RuntimeError("Cycle edge not found in original graph.")

    # --------------------------------------------------------
    # 4. MAIN LOOP — CANCEL NEGATIVE CYCLES
    # --------------------------------------------------------

    while True:
        R = build_residual(G, flow_dict)

        try:
            # Try to find a negative cycle in graph R
            cycle = negative_cycle_func(R, s, weight="weight")
        except nx.NetworkXError:
            cycle = None

        if not cycle:
            break  # terminate

        # ---- your bottleneck & augment logic, now "per SCC" ----
        bottleneck = float("inf")
        for i in range(len(cycle) - 1):
            u = cycle[i]
            v = cycle[i + 1]
            cap = R[u][v]["capacity"]
            if cap < bottleneck:
                bottleneck = cap
        if bottleneck <= 0:
            raise RuntimeError(
                "Residual bottleneck is non-positive (should not happen)."
            )

        augment_cycle(flow_dict, cycle, bottleneck)

    # --------------------------------------------------------
    # 5. COMPUTE FINAL MINIMUM COST
    # --------------------------------------------------------
    min_cost = 0
    for u, nbrs in flow_dict.items():
        for v, f in nbrs.items():
            if f > 0:  # only forward flows
                min_cost += f * G[u][v][weight]

    return flow_dict, min_cost
