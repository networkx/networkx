# -*- coding: utf-8 -*-
"""
Generalized flow algorithms on directed connected graphs.
"""

__authors__ = """Alexandre Costa, Georges Spyrides, Matheus Telles"""
__all__ = ['network_simplex_generalized']

from random import shuffle
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
    # For every node, add a dummy self loop edge with infinite-capacity and
    # infinite-weight. Those edges will be used to satisfy the node demands
    # and create an initial feasible solution.

    n = len(N)  # number of nodes
    for p, d in enumerate(D):
        S.append(p)
        T.append(p)
        if d < 0:  # Must be greater-than here. Zero-demand nodes must have
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
    C.extend(repeat(faux_inf, n))
    U.extend(repeat(faux_inf, n))

    # Construct the initial spanning tree.
    e = len(E)                     # number of edges
    edge = list(range(e, e+n))   # edges to parents
    size = list(repeat(1, n))      # subtree sizes
    next = list(range(n))          # next nodes in depth-first thread
    prev = list(range(n))          # previous nodes in depth-first thread
    last = list(range(n))          # last descendants in depth-first thread
    parent = list(range(n)) # parent nodes
    # edge flows
    x = list(chain(repeat(0, e), (-d/(1-Mu[e+i]) for i, d in enumerate(D))))
    # edge potentials
    pi = list(((faux_inf/(1-Mu[e+i]) for i, d in enumerate(D))))

    forest_root = list(range(n)) # augmented forest roots
    extra_edge = list(range(e, e+n)) # augmented forest extra edges

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
    print('# augmented forest roots\t', forest_root)
    print('# extra edges\t\t\t', extra_edge)

    ###########################################################################
    # Pivot loop
    ###########################################################################

    def reduced_cost(i):
        """Return the reduced cost of an edge i.
        """
        c = C[i] - pi[S[i]] + Mu[i]*pi[T[i]]
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
                if x[i] == 0:
                    p = S[i]
                    q = T[i]
                else:
                    p = T[i]
                    q = S[i]
                yield i, p, q
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
    
    #TODO new, discuss
    def is_root(p):
        """Returns true if node p is 
        """
        return p in forest_root
    
    #TODO - check in new data structure
    def trace_path(p):
        """Return the path from a given node p to its respective augmented tree root
        """
        Wn = [p]
        We = []
        while not is_root(p):
            We.append(edge[p])
            p = parent[p]
            Wn.append(p)
        return Wn, We

    def eliminate_redundancy(a, b):
        """ Takes two lists and crops their until it has only one element in common.
        """
        #only necessary for lists with more than two elements
        if len(a) <= 1 or len(b) <= 1:
            return a, b
        
        while a[-2] == b[-2]:
            del a[-1]
            del b[-1]
        return a, b


    #TODO - find cycle must return a boolean whether tree's were different 
    def find_cycle(i, p, q):
        """Return the nodes and edges on the cycle containing edge i == (p, q)
        when the latter is added to the spanning tree.

        The cycle is oriented in the direction from p to q.
        """
        Wn, We = trace_path(p)
        WnR, WeR = trace_path(q)

        #if found two different roots, we are going to work with two trees
        if Wn[-1] != WnR[-1]:
            return True, (Wn[-1], WnR[-1]), None, None

        tree_root = Wn[-1]
        Wn, WnR = eliminate_redundancy(Wn, WnR)
        We, WeR = eliminate_redundancy(We, WeR)

        Wn.reverse()
        We.reverse()
        We.append(i)
        del WnR[-1]
        Wn += WnR
        We += WeR
        return False, tree_root, Wn, We


    def residual_capacity(i, p):
        """Return the residual capacity of an edge i in the direction away
        from its endpoint p.
        """
        return U[i] - x[i] if S[i] == p else x[i]

    def find_leaving_edge(Wn1, We1, Wn2, We2):
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

    def update_potentials(i, h):
        """Update the potentials of the nodes in the tree rooted at node
        h and possessing an extra edge i.
        """        
        f, g = {q}, {q:0}, {q:1}
        for q in trace_subtree(h):
            p = prev[q]
            if p == parent[q]:
                j = edge[q]
                f[q] = (f[p] - C[j]) / Mu[j]
                g[q] = g[p] / Mu[j]
            elif q == parent[p]:
                j = edge[p]
                f[q] = (f[p] - C[j]) * Mu[j]
                g[q] = g[p] * Mu[j]

        theta = (C[i] - f[S[i]] + Mu[i] * f[T[i]]) / (g[S[i]] - Mu[i] * g[T[i]])

        for q in trace_subtree(h):
            pi[q] = f[q] + g[q] * theta

    #TODO new, discuss
    def find_extra_edge(root):
        """ Returns the extra edge belonging to the tree rooted at 'root'
        """
        edge_id = extra_edge[forest_root.index(root)]
        return edge_id, S[edge_id], T[edge_id]

    def update_flows(i, h):
        """Update the flows of the nodes in the tree rooted at a node
        h and possessing an extra edge i.
        """
        remaining, f, g = {}, {}, {}
        for q in trace_subtree(h):
            remaining[q] = size[q]
            f[q] = -D[q]
            g[q] = 0
        g[S[i]] = -1
        g[T[i]] = Mu[i]

        while list(remaining.keys()) != [h]:
            q = -1
            for node, count in remaining.items():
                if count > 1:
                    continue
                q = node
                break
            
            p = prev[q]
            if q == parent[p]:
                j = edge[p]
                f[p] += f[q] * Mu[j]
                g[p] += g[q] * Mu[j]            
            elif p == parent[q]:
                j = edge[q]
                f[p] += f[q] / Mu[j]
                g[p] += g[q] / Mu[j]

            remaining[p] -= 1
            del remaining[q]

        theta = f[h] / g[h]

        for q in trace_subtree(h):
            p = prev[q]
            if q == parent[p]:
                j = edge[p]
                x[j] = f[q] + g[q] * theta
            elif p == parent[q]:
                j = edge[q]
                x[j] = -(f[q] + g[q] * theta) / Mu[j]

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
    for enter_edge_id, enter_edge_origin, enter_edge_destination in find_entering_edges():
        print('######################################################')
        print('# Pivot Loop #########################################')
        print('# entering edges\t', enter_edge_id,
                                    enter_edge_origin,
                                    enter_edge_destination)

        #TODO - create enlongated variables names and create structure to deal with two cycles
        different_trees, cycle_root, Wn1, We1 = find_cycle(enter_edge_id,
                                                            enter_edge_origin,
                                                            enter_edge_destination)

        print('# different trees: ', different_trees)
        print('# cycle_root: ', cycle_root)
        print('# Wn1: ', Wn1)
        print('# We1: ', We1)

        if different_trees:
            #assert len(cycle_root) == 2
            extra_edge_1_id, extra_edge_1_origin, extra_edge_1_destination = find_extra_edge(cycle_root[0])
            _, _, Wn1, We1 = find_cycle(extra_edge_1_id,
                                        extra_edge_1_origin,
                                        extra_edge_1_destination)
            extra_edge_2_id, extra_edge_2_origin, extra_edge_2_destination = find_extra_edge(cycle_root[1])
            _, _, Wn2, We2 = find_cycle(extra_edge_2_id,
                                        extra_edge_2_origin,
                                        extra_edge_2_destination)
        else:
            extra_edge_id, extra_edge_origin, extra_edge_destination = find_extra_edge(cycle_root)
            _, _, Wn2, We2 = find_cycle(extra_edge_id,
                                        extra_edge_origin,
                                        extra_edge_destination)
        print('# find cycle\t\t', Wn1, We1, Wn2, We2)

        leav_edge_id, leav_edge_origin, leav_edge_destination = find_leaving_edge(Wn1, We1, Wn2, We2)
        print('# leaving edge\t\t', leav_edge_id, leav_edge_origin, leav_edge_destination)

        augment_flow(Wn, We, residual_capacity(leav_edge_id, leav_edge_origin))
        print('# augment flow\t\t', Wn, We)

        if enter_edge_id != leav_edge_id:  # Do nothing more if the entering edge is the same as the
                    # the leaving edge.
            if parent[leav_edge_destination] != leav_edge_origin:
                # Ensure that s is the parent of t.
                leav_edge_origin, leav_edge_destination = leav_edge_destination, leav_edge_origin
            if We.index(enter_edge_id) > We.index(leav_edge_id):
                # Ensure that q is in the subtree rooted at t.
                enter_edge_origin, enter_edge_destination = enter_edge_destination, enter_edge_origin

            remove_edge(leav_edge_origin, leav_edge_destination)
            make_root(enter_edge_destination)
            add_edge(enter_edge_id, enter_edge_origin, enter_edge_destination)
            update_potentials(enter_edge_id, enter_edge_origin, enter_edge_destination)

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
