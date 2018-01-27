# -*- coding: utf-8 -*-
"""
Generalized flow algorithms on directed connected graphs.
"""

__authors__ = """Alexandre Costa, Georges Spyrides, Matheus Telles"""
__all__ = ['network_simplex_generalized']

from itertools import chain, islice, repeat
from math import ceil, sqrt
import networkx as nx
from networkx.utils import not_implemented_for

try:
    from itertools import izip as zip
except ImportError:
    pass
try:
    range = xrange
except NameError:
    pass


@not_implemented_for('undirected')
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

    multigraph = G.is_multigraph()
    S = []  # edge sources
    T = []  # edge targets
    if multigraph:
        K = []  # edge keys
    E = {}  # edge indices
    U = []  # edge capacities
    C = []  # edge weights
    Mu = []  # edge multipliers

    if not multigraph:
        edges = G.edges(data=True)
    else:
        edges = G.edges(data=True, keys=True)
    edges = (e for e in edges
             if e[0] != e[1] and e[-1].get(capacity, inf) != 0)
    for i, e in enumerate(edges):
        S.append(I[e[0]])
        T.append(I[e[1]])
        if multigraph:
            K.append(e[2])
        E[e[:-1]] = i
        U.append(e[-1].get(capacity, inf))
        C.append(e[-1].get(weight, 0))
        Mu.append(e[-1].get(multiplier, 1))

    for e, c, mu in zip(E, C, Mu):
        if abs(mu) == inf or mu <= 0:
            raise nx.NetworkXError('edge %r has invalid multiplier' % (e,))
        if abs(c) == inf:
            raise nx.NetworkXError('edge %r has infinite weight' % (e,))
    if not multigraph:
        edges = nx.selfloop_edges(G, data=True)
    else:
        edges = nx.selfloop_edges(G, data=True, keys=True)
    for e in edges:
        if abs(e[-1].get(weight, 0)) == inf:
            raise nx.NetworkXError('edge %r has infinite weight' % (e[:-1],))

    ###########################################################################
    # Quick infeasibility detection
    ###########################################################################

    for e, u in zip(E, U):
        if u < 0:
            raise nx.NetworkXUnfeasible('edge %r has negative capacity' % (e,))
    if not multigraph:
        edges = nx.selfloop_edges(G, data=True)
    else:
        edges = nx.selfloop_edges(G, data=True, keys=True)
    for e in edges:
        if e[-1].get(capacity, inf) < 0:
            raise nx.NetworkXUnfeasible(
                'edge %r has negative capacity' % (e[:-1],))

    ###########################################################################
    # Initialization
    ###########################################################################

    # Add a dummy node -1 and connect all existing nodes to it with infinite-
    # capacity dummy edges. Node -1 will serve as the root of the
    # spanning tree of the network simplex method. The new edges will used to
    # trivially satisfy the node demands and create an initial strongly
    # feasible spanning tree.
    n = len(N)  # number of nodes
    for p, d in enumerate(D):
        if d > 0:  # Must be greater-than here. Zero-demand nodes must have
                   # edges pointing towards the root to ensure strong
                   # feasibility.
            S.append(-1)
            T.append(p)
        else:
            S.append(p)
            T.append(-1)

    # DONE: check if Mu positive values should multiply here
    mu_product = 1
    for i in [mu for mu in Mu if mu > 1]:
        mu_product *= i

    faux_inf = 3 * mu_product * max(chain([sum(u for u in U if u < inf),
                              sum(abs(c) for c in C)],
                             (abs(d) for d in D))) or 1
    C.extend(repeat(faux_inf, n))
    U.extend(repeat(faux_inf, n))

    # Construct the initial spanning tree.
    e = len(E)                                           # number of edges
    x = list(chain(repeat(0, e), (abs(d) for d in D)))   # edge flows
    pi = [faux_inf if d <= 0 else -faux_inf for d in D]  # node potentials
    parent = list(chain(repeat(-1, n), [None]))  # parent nodes
    edge = list(range(e, e + n))                 # edges to parents
    size = list(chain(repeat(1, n), [n + 1]))    # subtree sizes
    next = list(chain(range(1, n), [-1, 0]))     # next nodes in depth-first thread
    prev = list(range(-1, n))                    # previous nodes in depth-first thread
    last = list(chain(range(n), [n - 1]))        # last descendants in depth-first thread

    print('######################################################')
    print('# Tree Variables #####################################')
    print('# number of edges\t\t', e)
    print('# edge flows\t\t\t', x)
    print('# node potentials\t\t', pi)
    print('# parent nodes\t\t\t', parent)
    print('# edges to parents\t\t', edge)
    print('# subtree sizes\t\t\t', size)
    print('# next nodes in dfs thread\t', next)
    print('# previous nodes in dfs thread\t', prev)
    print('# last descendants in dfs thread', last)

    ###########################################################################
    # Pivot loop
    ###########################################################################

    def reduced_cost(i):
        """Return the reduced cost of an edge i.
        """
        c = C[i] - pi[S[i]] + pi[T[i]]
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
        B = int(ceil(sqrt(e)))  # pivot block size
        M = (e + B - 1) // B    # number of blocks needed to cover all edges
        m = 0                   # number of consecutive blocks without eligible
                                # entering edges
        f = 0                   # first edge in block
        while m < M:
            # Determine the next block of edges.
            l = f + B
            if l <= e:
                edges = range(f, l)
            else:
                l -= e
                edges = chain(range(f, e), range(l))
            f = l
            # Find the first edge with the lowest reduced cost.
            i = min(edges, key=reduced_cost)
            c = reduced_cost(i)
            if c >= 0:
                # No entering edge found in the current block.
                m += 1
            else:
                # Entering edge found.
                if x[i] == 0:
                    p = S[i]
                    q = T[i]
                else:
                    p = T[i]
                    q = S[i]
                yield i, p, q
                m = 0
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
        """Return the nodes and edges on the path from node p to its ancestor
        w.
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


    def residual_capacity(i, p):
        """Return the residual capacity of an edge i in the direction away
        from its endpoint p.
        """
        return U[i] - x[i] if S[i] == p else x[i]

    def find_leaving_edge(Wn, We):
        """Return the leaving edge in a cycle represented by Wn and We.
        """
        j, s = min(zip(reversed(We), reversed(Wn)),
                   key=lambda i_p: residual_capacity(*i_p))
        t = T[j] if S[j] == s else S[j]
        return j, s, t

    def augment_flow(Wn, We, f):
        """Augment f units of flow along a cycle represented by Wn and We.
        """
        for i, p in zip(We, Wn):
            if S[i] == p:
                x[i] += f
            else:
                x[i] -= f

    def trace_subtree(p):
        """Yield the nodes in the subtree rooted at a node p.
        """
        yield p
        l = last[p]
        while p != l:
            p = next[p]
            yield p

    def remove_edge(s, t):
        """Remove an edge (s, t) where parent[t] == s from the spanning tree.
        """
        size_t = size[t]
        prev_t = prev[t]
        last_t = last[t]
        next_last_t = next[last_t]
        # Remove (s, t).
        parent[t] = None
        edge[t] = None
        # Remove the subtree rooted at t from the depth-first thread.
        next[prev_t] = next_last_t
        prev[next_last_t] = prev_t
        next[last_t] = t
        prev[t] = last_t
        # Update the subtree sizes and last descendants of the (old) acenstors
        # of t.
        while s is not None:
            size[s] -= size_t
            if last[s] == last_t:
                last[s] = prev_t
            s = parent[s]

    def make_root(q):
        """Make a node q the root of its containing subtree.
        """
        ancestors = []
        while q is not None:
            ancestors.append(q)
            q = parent[q]
        ancestors.reverse()
        for p, q in zip(ancestors, islice(ancestors, 1, None)):
            size_p = size[p]
            last_p = last[p]
            prev_q = prev[q]
            last_q = last[q]
            next_last_q = next[last_q]
            # Make p a child of q.
            parent[p] = q
            parent[q] = None
            edge[p] = edge[q]
            edge[q] = None
            size[p] = size_p - size[q]
            size[q] = size_p
            # Remove the subtree rooted at q from the depth-first thread.
            next[prev_q] = next_last_q
            prev[next_last_q] = prev_q
            next[last_q] = q
            prev[q] = last_q
            if last_p == last_q:
                last[p] = prev_q
                last_p = prev_q
            # Add the remaining parts of the subtree rooted at p as a subtree
            # of q in the depth-first thread.
            prev[p] = last_q
            next[last_q] = p
            next[last_p] = q
            prev[q] = last_p
            last[q] = last_p

    def add_edge(i, p, q):
        """Add an edge (p, q) to the spanning tree where q is the root of a
        subtree.
        """
        last_p = last[p]
        next_last_p = next[last_p]
        size_q = size[q]
        last_q = last[q]
        # Make q a child of p.
        parent[q] = p
        edge[q] = i
        # Insert the subtree rooted at q into the depth-first thread.
        next[last_p] = q
        prev[q] = last_p
        prev[next_last_p] = last_q
        next[last_q] = next_last_p
        # Update the subtree sizes and last descendants of the (new) ancestors
        # of q.
        while p is not None:
            size[p] += size_q
            if last[p] == last_p:
                last[p] = last_q
            p = parent[p]

    def update_potentials(i, p, q):
        """Update the potentials of the nodes in the subtree rooted at a node
        q connected to its parent p by an edge i.
        """
        if q == T[i]:
            d = pi[p] - C[i] - pi[q]
        else:
            d = pi[p] + C[i] - pi[q]
        for q in trace_subtree(q):
            pi[q] += d

    print('######################################################')
    print('# Data structures ####################################')
    print('# nodes\t\t\t', N)
    print('# node indices\t\t', I)
    print('# node demands\t\t', D)
    print('# edge sources\t\t', S)
    print('# edge targets\t\t', T)
    if multigraph:
        print('# edge keys\t\t', K)
    print('# edge indices\t\t', E)
    print('# edge capacities\t', U)
    print('# edge weights\t\t', C)
    print('# edge multipliers\t', Mu)

    # Pivot loop
    for i, p, q in find_entering_edges():
        print('######################################################')
        print('# Pivot Loop #########################################')
        print('# entering edges\t', i, p, q)
        Wn, We = find_cycle(i, p, q)
        print('# find cycle\t\t', Wn, We)
        j, s, t = find_leaving_edge(Wn, We)
        print('# leaving edge\t\t', j, s, t)
        augment_flow(Wn, We, residual_capacity(j, s))
        print('# augment flow\t\t', Wn, We)
        if i != j:  # Do nothing more if the entering edge is the same as the
                    # the leaving edge.
            if parent[t] != s:
                # Ensure that s is the parent of t.
                s, t = t, s
            if We.index(i) > We.index(j):
                # Ensure that q is in the subtree rooted at t.
                p, q = q, p
            remove_edge(s, t)
            make_root(q)
            add_edge(i, p, q)
            update_potentials(i, p, q)

    ###########################################################################
    # Infeasibility and unboundedness detection
    ###########################################################################

    if any(x[i] != 0 for i in range(-n, 0)):
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
    if not multigraph:
        for e in zip(S, T, x):
            add_entry(e)
        edges = G.edges(data=True)
    else:
        for e in zip(S, T, K, x):
            add_entry(e)
        edges = G.edges(data=True, keys=True)
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
