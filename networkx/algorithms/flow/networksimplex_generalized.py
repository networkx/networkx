# -*- coding: utf-8 -*-
"""
Generalized flow algorithms on directed connected graphs.
"""

__authors__ = """Alexandre Costa, Georges Spyrides, Matheus Telles"""
__all__ = ['network_simplex_generalized']

from collections import OrderedDict
from itertools import chain, islice, repeat
from math import ceil, sqrt
import networkx as nx
from networkx.utils import not_implemented_for
from random import shuffle, seed

# UNDO
seed(4) # choose BD as second entering edge
# seed(1) # choose AC as second entering edge

try:
    from itertools import izip as zip
except ImportError:
    pass
try:
    range = xrange
except NameError:
    pass


@not_implemented_for('undirected', 'multigraph')
def network_simplex_generalized(G, demand='demand', capacity='capacity', weight='weight', multiplier='multiplier'):
    ###########################################################################
    # Problem essentials extraction and sanity check
    ###########################################################################

    if len(G) == 0:
        raise nx.NetworkXError('graph has no nodes')

    # Number all nodes and edges and hereafter reference them using ONLY their
    # numbers

    N = list(G)                                # nodes
    I = {u: i for i, u in enumerate(N)}        # node indices
    D = [G.nodes[u].get(demand, 0) for u in N]  # node demands

    inf = float('inf')
    for p, b in zip(N, D):
        if abs(b) == inf:
            raise nx.NetworkXError('node %r has infinite demand' % (p,))

    S = []  # edge sources
    T = []  # edge targets
    E = {}  # edge indices
    U = []  # edge capacities
    C = []  # edge weights
    Mu = []  # edge multipliers

    edges = G.edges(data=True)
    edges = (e for e in edges
             if e[0] != e[1] and e[-1].get(capacity, inf) != 0)
    for i, e in enumerate(edges):
        S.append(I[e[0]])
        T.append(I[e[1]])
        E[e[:-1]] = i
        U.append(e[-1].get(capacity, inf))
        C.append(e[-1].get(weight, 0))
        Mu.append(e[-1].get(multiplier, 1))

    for e, c, mu in zip(E, C, Mu):
        if abs(mu) == inf or mu <= 0:
            raise nx.NetworkXError('edge %r has invalid multiplier' % (e,))
        if abs(c) == inf:
            raise nx.NetworkXError('edge %r has infinite weight' % (e,))

    edges = nx.selfloop_edges(G, data=True)
    for e in edges:
        if abs(e[-1].get(weight, 0)) == inf:
            raise nx.NetworkXError('edge %r has infinite weight' % (e[:-1],))

    ###########################################################################
    # Quick infeasibility detection
    ###########################################################################

    for e, u in zip(E, U):
        if u < 0:
            raise nx.NetworkXUnfeasible('edge %r has negative capacity' % (e,))
    edges = nx.selfloop_edges(G, data=True)
    for e in edges:
        if e[-1].get(capacity, inf) < 0:
            raise nx.NetworkXUnfeasible('edge %r has negative capacity' % (e[:-1],))

    ###########################################################################
    # Initialization
    ###########################################################################
    # For every node, add a dummy self loop edge with infinite-capacity and
    # infinite-weight. Those edges will be used to satisfy the node demands
    # and create an initial feasible solution.

    n = len(N)  # number of nodes
    for p, d in enumerate(D):
        S.append(p)
        T.append(p)
        if d > 0:  # Must be greater-than here. Zero-demand nodes must have
                   # edges pointing towards the root to ensure strong
                   # feasibility.
            Mu.append(0.5)
        else:
            Mu.append(2)

    # DONE: check if Mu positive values should multiply here
    mu_product = 1
    for i in [mu for mu in Mu if mu > 1]:
        mu_product *= i

    faux_inf = 3 * mu_product * max(chain([sum(u for u in U if u < inf),
                                           sum(abs(c) for c in C)],
                                          (abs(d) for d in D))) or 1
    # UNDO
    faux_inf = 1000
    C.extend(repeat(faux_inf, n))
    U.extend(repeat(faux_inf*faux_inf, n))

    # Construct the initial augmented forest
    e = len(E)                     # number of edges
    edge = list(repeat(None, n))   # edges to parents
    size = list(repeat(1, n))      # subtree sizes
    next = list(range(n))          # next nodes in depth-first thread
    prev = list(range(n))          # previous nodes in depth-first thread
    last = list(range(n))          # last descendants in depth-first thread
    parent = list(repeat(None, n)) # parent nodes
    x = list(chain(repeat(0, e), (d/(1-Mu[e+i]) for i, d in enumerate(D)))) # edge flows
    pi = list(((faux_inf/(1-Mu[e+i]) for i, d in enumerate(D)))) # edge potentials

    root = list(range(n))     # root of the augmented forest cotaining node
    extra = dict((i,i+e) for i in range(n)) # augmented forest extra edges

    upper = set()
    lower = set(range(e))
    forest = set(range(e,e+n))

    ###########################################################################
    # Pivot loop
    ###########################################################################

    def reduced_cost(i):
        """Return the reduced cost of an edge i.
        """
        c = C[i] - pi[S[i]] + Mu[i] * pi[T[i]]
        return c if x[i] == 0 else -c

    def find_entering_edges():
        """Yield entering edges until none can be found.
        """
        if e == 0:
            return

        # Entering edges are found by combining Dantzig's rule and Bland's
        # rule. The edges are cyclically grouped into blocks of size B. Within
        # each block, Dantzig's rule is applied to find an entering edge. The
        # blocks to search is determined following Bland's rule.
        B = int(ceil(sqrt(e))) # pivot block size
        M = (e + B - 1) // B   # number of blocks needed to cover all edges
        m = 0                  # number of consecutive blocks without eligible entering edges

        # Iterate through blocks in a random order to stimulate finding faraway edges
        blocks_random = list(range(M))
        shuffle(blocks_random)

        while m < M:
            # Determine the next block of edges.
            block_index = blocks_random[m]
            f = B * block_index # first edge in block
            l = f + B           # last edge in block
            if l <= e:
                edges = range(f, l)
            else:
                l -= e
                edges = chain(range(f, e), range(l))

            # Find the first edge with the lowest reduced cost.
            i = min(edges, key=reduced_cost)
            c = reduced_cost(i)
            if c >= 0:
                # No entering edge found in the current block.
                m += 1
            else:
                # Entering edge found.
                yield i
                m = 0
                shuffle(blocks_random)
        # All edges have nonnegative reduced costs. The current flow is
        # optimal.

    def find_apex(p, q):
        """Find the lowest common ancestor of nodes p and q in the spanning
        tree.
        """
        size_p = size[p]
        size_q = size[q]
        while True:
            while size_p < size_q:
                p = parent[p]
                size_p = size[p]
            while size_p > size_q:
                q = parent[q]
                size_q = size[q]
            if size_p == size_q:
                if p != q:
                    p = parent[p]
                    size_p = size[p]
                    q = parent[q]
                    size_q = size[q]
                else:
                    return p

    def trace_path(p, w):
        """Return the path from a given node p to its respective augmented tree root
        """
        Wn = [p]
        We = []
        while p != w:
            We.append(edge[p])
            p = parent[p]
            Wn.append(p)
        return Wn, We

    def find_cycle(i, p, q):
        """Return the nodes and edges on the cycle containing edge i == (p, q)
        when the latter is added to the spanning tree.

        The cycle is oriented in the direction from p to q.
        """
        w = find_apex(p, q)
        Wn, We = trace_path(p, w)
        Wn.reverse()
        We.reverse()
        We.append(i)
        WnR, WeR = trace_path(q, w)
        del WnR[-1]
        Wn += WnR
        We += WeR
        return Wn, We

    def trace_subtree(p):
        """Yield the nodes in the subtree rooted at a node p.
        """
        yield p
        l = last[p]
        while p != l:
            p = next[p]
            yield p

    def compute_flows(d, h):
        """Compute the flows of the nodes in the tree rooted at a node h
        given demands d.
        """
        h = root[h]
        i = extra[h]
        remaining, f, g = {}, {}, {}

        for q in trace_subtree(h):
            remaining[q] = size[q]
            f[q] = d[q]
            g[q] = 0

        g[S[i]] = -1
        g[T[i]] = Mu[i]

        while list(remaining.keys()) != [h]:
            to_compute = [node for node, count in remaining.items()
                          if (count < 2 or len(remaining) == 2) and node != h]
            for q in to_compute:
                p = parent[q]
                j = edge[q]

                if S[j] == q:
                    f[p] += f[q] * Mu[j]
                    g[p] += g[q] * Mu[j]
                elif S[j] == p:
                    f[p] += f[q] / Mu[j]
                    g[p] += g[q] / Mu[j]
                    f[q] = -f[q] / Mu[j]
                    g[q] = -g[q] / Mu[j]

                remaining[p] -= 1
                del remaining[q]

        # if self loop node
        if h == S[i] and S[i] == T[i] and i in forest:
            # if self loop with demand on previous node
            if d[prev[h]] != 0:
                if prev[h] != h:
                    f[h] = -d[h] - d[prev[h]]
                else:
                    f[h] = -d[prev[h]]
            else:
                f[h] = -d[h]
            g[h] = (1 - Mu[i])

        theta =  -f[h] / g[h]

        y = {edge[q]:f[q] + g[q] * theta
             for q in trace_subtree(h) if q != h}

        y[i] = theta

        return y

    def maximum_additional_flow(i, y):
        """Return the maximum additional flow of an edge i, given a hipotetic flow rate
        of y from the entering edge
        """
        if y > 0:
            return (U[i] - x[i]) / y
        elif y < 0:
            return x[i] / -y
        else:
            return faux_inf

    def find_leaving_edge(j):
        """Return the leaving edge of a augmented tree with root h,
        given an entering edge j. Also returns the amount of flow necessary
        on edge j for the chosen edge to leave.
        """
        d = {q:0 for q in trace_subtree(root[S[j]])}
        # Leaving edge may have disconnected the old augmented tree
        if root[S[j]] != root[T[j]]:
            d2 = {q:0 for q in trace_subtree(root[T[j]])}
            d.update(d2)
        d[S[j]], d[T[j]] = (-1., Mu[j]) if x[j] == 0 else (1/Mu[j], -1.)

        y = compute_flows(d, root[S[j]])
        if root[S[j]] != root[T[j]]:
            y2 = compute_flows(d, root[T[j]])
            y.update(y2)
        y[j] = 1. if x[j] == 0 else -1.
        print("demand", d)
        print("y",y)
        print("Maximum flow",[(i_y[0], maximum_additional_flow(*i_y)) for i_y in y.items()])
        leaving_edge, flow = min(y.items(),
                                 key=lambda i_y: maximum_additional_flow(*i_y))
        sigma = maximum_additional_flow(leaving_edge, flow)

        #if y[leaving_edge] < 0:
        #    sigma *= -1

        return leaving_edge, sigma

    def update_potentials(h):
        """Update the potentials of the nodes in the tree rooted at node h
        """
        i = extra[root[h]]
        f, g = {h:0}, {h:1}
        for q in trace_subtree(h):
            p = parent[q]
            j = edge[q]
            if j == None or p == None:
                continue
            if S[j] == p:
                f[q] = (f[p] - C[j]) / Mu[j]
                g[q] = g[p] / Mu[j]
            elif S[j] == q:
                f[q] = f[p] * Mu[j] + C[j]
                g[q] = g[p] * Mu[j]

        theta = (C[i] - f[S[i]] + Mu[i] * f[T[i]]) / (g[S[i]] - Mu[i] * g[T[i]])

        for q in trace_subtree(h):
            pi[q] = f[q] + g[q] * theta

    def update_flows(h):
        d = {q:D[q] for q in trace_subtree(h)}
        for q in trace_subtree(h):
            if edge[q] == None:
                continue
            x[edge[q]] = 0
        x[extra[h]] = 0
        for e in lower:
            x[e] = 0
        for e in upper:
            x[e] = U[e]
            if S[e] in d:
                d[S[e]] -= U[e]
            if T[e] in d:
                d[T[e]] += Mu[e] * U[e]
        y = compute_flows(d, h)
        for q, flow in y.items():
            x[q] += flow

    def update_tree_indices(i, j):
        """
        """
        edge_ids = [edge[q] for q in trace_subtree(root[S[i]]) if edge[q] != None] + \
                   [extra[root[S[i]]]]

        # Entering arc connects two augmented trees
        if root[S[i]] != root[T[i]]:
            edge_ids += [edge[q] for q in trace_subtree(root[T[i]]) if edge[q]] + \
                        [extra[root[T[i]]]]
            del extra[root[T[i]]]
        del extra[root[S[i]]]
        edge_ids = list(set(edge_ids))
        edge_ids.append(i)
        edge_ids.remove(j)

        source_ids = set(S[edge_id] for edge_id in edge_ids)
        target_ids = set(T[edge_id] for edge_id in edge_ids)
        node_ids = source_ids | target_ids

        adjacencies = {node_id:{} for node_id in node_ids}
        for edge_id in edge_ids:
            adjacencies[S[edge_id]][T[edge_id]] = edge_id
            adjacencies[T[edge_id]][S[edge_id]] = edge_id

        for node_id in node_ids:
            edge[node_id] = None
            size[node_id] = None
            next[node_id] = None
            prev[node_id] = None
            last[node_id] = None
            parent[node_id] = None
            root[node_id] = None

        def dfs(graph, start_id, root_id, visited):
            last_node_id = start_id
            total_nodes = 1

            visited[start_id] = True
            for node_id, edge_id in graph[start_id].items():
                if node_id in visited:
                    if parent[start_id] != node_id:
                        extra[root_id] = edge_id
                    continue
                parent[node_id] = start_id
                edge[node_id] = edge_id
                _, n_nodes, last_node_id = dfs(graph, node_id, root_id, visited)
                total_nodes += n_nodes

            root[start_id] = root_id
            last[start_id] = last_node_id
            size[start_id] = total_nodes
            return visited, total_nodes, last_node_id

        # Leaving edge may disconnect the graph
        global_visited = OrderedDict()
        for node_id in node_ids:
            if node_id in global_visited:
                continue
            visited = OrderedDict()
            visited, n_nodes, _ = dfs(adjacencies, node_id, node_id, visited)
            global_visited.update(visited)
            visited = list(visited)
            for i, node in enumerate(visited):
                prev[node] = visited[(i-1)%n_nodes]
                next[node] = visited[(i+1)%n_nodes]

    def print_augmented_forest_info():
        print('######################################################')
        print('# Forest Variables #####################################')
        print('# number of edges\t\t', e)
        print('# edge flows\t\t\t', x)
        print('# node potentials\t\t', pi)
        print('# parent nodes\t\t\t', parent)
        print('# edges to parents\t\t', edge)
        print('# subtree sizes\t\t\t', size)
        print('# next nodes in dfs thread\t', next)
        print('# previous nodes in dfs thread\t', prev)
        print('# last descendants in dfs thread', last)
        print('# augmented forest roots\t', root)
        print('# extra edges\t\t\t', extra)
        print('# Edges in upper\t\t\t', upper)
        print('# Edges in lower\t\t\t', lower)
        print('# Edges in forest\t\t\t', forest)

    print('######################################################')
    print('# Data structures ####################################')
    print('# nodes\t\t\t', N)
    print('# node indices\t\t', I)
    print('# node demands\t\t', D)
    print('# edge sources\t\t', S)
    print('# edge targets\t\t', T)
    print('# edge indices\t\t', E)
    print('# edge capacities\t', U)
    print('# edge weights\t\t', C)
    print('# edge multipliers\t', Mu)

    # Pivot loop
    for i in find_entering_edges():
        print_augmented_forest_info()
        print('######################################################')
        print('# Pivot Loop #########################################')
        print('# entering edges (i)\t', i)
        j, sigma = find_leaving_edge(i)
        print('# leaving edges (i, sigma)\t', j, sigma)

        forest.add(i)
        forest.remove(j)
        upper -= set([i])
        lower -= set([i])
        # Leaving edge is bounded above
        if sigma > 0:
            upper.add(j)
        else:
            lower.add(j)

        if i != j:
            update_tree_indices(i, j)

        # It's only necessary to update new augmented tree
        update_potentials(root[S[j]])
        if any(pi[index] > 0 for index in range(0, n)):
            update_flows(root[S[j]])
        # Leaving edge may have disconnected the old augmented tree
        if root[S[j]] != root[T[j]]:
            update_potentials(root[T[j]])
            if any(pi[index] > 0 for index in range(0, n)):
                update_flows(root[T[j]])


    print_augmented_forest_info()

    ###########################################################################
    # Infeasibility and unboundedness detection
    ###########################################################################

    if any(x[i] != 0 for i in range(0, e)):
        raise nx.NetworkXUnfeasible('no flow satisfies all node demands')

    if (any(x[i] * 2 >= faux_inf for i in range(e)) or
        any(e[-1].get(capacity, inf) == inf and e[-1].get(weight, 0) < 0
            for e in nx.selfloop_edges(G, data=True))):
        raise nx.NetworkXUnbounded(
            'negative cycle with infinite capacity found')

    ###########################################################################
    # Flow cost calculation and flow dict construction
    ###########################################################################

    del x[e:]
    flow_cost = sum(c * x for c, x in zip(C, x))
    flow_dict = {n: {} for n in N}

    def add_entry(e):
        """Add a flow dict entry.
        """
        d = flow_dict[e[0]]
        for k in e[1:-2]:
            try:
                d = d[k]
            except KeyError:
                t = {}
                d[k] = t
                d = t
        d[e[-2]] = e[-1]

    S = (N[s] for s in S)  # Use original nodes.
    T = (N[t] for t in T)  # Use original nodes.
    for e in zip(S, T, x):
        add_entry(e)
    edges = G.edges(data=True)
    for e in edges:
        if e[0] != e[1]:
            if e[-1].get(capacity, inf) == 0:
                add_entry(e[:-1] + (0,))
        else:
            c = e[-1].get(weight, 0)
            if c >= 0:
                add_entry(e[:-1] + (0,))
            else:
                u = e[-1][capacity]
                flow_cost += c * u
                add_entry(e[:-1] + (u,))

    return flow_cost, flow_dict
