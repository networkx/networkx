#    Copyright (C) 2019 by
#    Balint Tillman <tillman.balint@gmail.com>
#    All rights reserved.
#    BSD license.
#
# Author:  Balint Tillman (tillman.balint@gmail.com)
"""Generate graphs with a given directed joint degree """
from __future__ import division

import networkx as nx
from networkx.utils import py_random_state

__all__ = ['is_valid_directed_joint_degree',
           'directed_joint_degree_graph']


def test_is_valid_directed_joint_degree():

    in_degrees = [0, 1, 1, 2]
    out_degrees = [1, 1, 1, 1]
    nkk = {1: {1: 2, 2: 2}}
    assert(is_valid_directed_joint_degree(in_degrees, out_degrees, nkk))

    # not realizable, values are not integers.
    nkk = {1: {1: 1.5, 2: 2.5}}
    assert(not is_valid_directed_joint_degree(in_degrees, out_degrees, nkk))

    # not realizable, number of edges between 1-2 are insufficient.
    nkk = {1: {1: 2, 2: 1}}
    assert(not is_valid_directed_joint_degree(in_degrees, out_degrees, nkk))

    # not realizable, in/out degree sequences have different number of nodes.
    out_degrees = [1, 1, 1]
    nkk = {1: {1: 2, 2: 2}}
    assert(not is_valid_directed_joint_degree(in_degrees, out_degrees, nkk))

    # not realizable, degree seqeunces have fewer than required nodes.
    in_degrees = [0, 1, 2]
    assert(not is_valid_directed_joint_degree(in_degrees, out_degrees, nkk))


def test_directed_joint_degree_graph(n=15, m=100, ntimes=1000):
    for _ in range(ntimes):

        # generate gnm random graph and calculate its joint degree.
        g = nx.gnm_random_graph(n, m, None, directed=True)

        # in-degree seqeunce of g as a list of integers.
        in_degrees = list(dict(g.in_degree()).values())
        # out-degree sequence of g as a list of integers.
        out_degrees = list(dict(g.out_degree()).values())
        nkk = nx.degree_mixing_dict(g)

        # generate simple directed graph with given degree sequence and joint
        # degree matrix.
        G = directed_joint_degree_graph(in_degrees, out_degrees, nkk)

        # assert degree sequence correctness.
        assert(in_degrees == list(dict(G.in_degree()).values()))
        assert(out_degrees == list(dict(G.out_degree()).values()))
        # assert joint degree matrix correctness.
        assert(nkk == nx.degree_mixing_dict(G))


def is_valid_directed_joint_degree(in_degrees, out_degrees, nkk):
    """ Checks whether the given directed joint degree input (in/out degree
        sequences, nkk) is realizable as a simple directed graph by evaluating
        necessary and sufficient conditions.

    Here is the list of conditions that the inputs need to satisfy for
    simple graph realizability:
    - Condition 0: in_degrees and out_degrees have the same length
    - Condition 1: nkk[k][l]  is integer for all k,l
    - Condition 2: sum(nkk[k])/k = number of nodes with partition id k, is an
                   integer and matching degree sequence
    - Condition 3: number of edges and non-chords between k and l cannot exceed
                   maximum possible number of edges

    Parameters
    ----------
    in_degrees :  list of integers
        in degree sequence contains the in degrees of nodes.
    out_degrees : list of integers
        out degree sequence contains the out degrees of nodes.
    nkk  :  dictionary of dictionary of integers
        directed joint degree dictionary. for nodes of out degree k (first
        level of dict) and nodes of in degree l (seconnd level of dict)
        describes the number of edges.

    Returns
    -------
    boolean
        returns true if given input is realizable, else returns false.

    References
    ----------
    [1] B. Tillman, A. Markopoulou, C. T. Butts & M. Gjoka,
        "Construction of Directed 2K Graphs". In Proc. of KDD 2017.
    """
    V = {}  # number of nodes with in/out degree.
    forbidden = {}
    if len(in_degrees) != len(out_degrees):
        return False

    for idx in range(0, len(in_degrees)):
        i = in_degrees[idx]
        o = out_degrees[idx]
        V[(i, 0)] = V.get((i, 0), 0) + 1
        V[(o, 1)] = V.get((o, 1), 0) + 1

        forbidden[(o, i)] = forbidden.get((o, i), 0) + 1

    S = {}  # number of edges going from in/out degree nodes.
    for k in nkk:
        for l in nkk[k]:
            val = nkk[k][l]
            if not float(val).is_integer():  # condition 1
                return False

            if val > 0:
                S[(k, 1)] = S.get((k, 1), 0) + val
                S[(l, 0)] = S.get((l, 0), 0) + val
                # condition 3
                if val + forbidden.get((k, l), 0) > V[(k, 1)] * V[(l, 0)]:
                    return False

    for s in S:
        if not float(S[s]) / s[0] == V[s]:  # condition 2
            return False

    # if all conditions abive have been satisfied then the input nkk is
    # realizable as a simple graph.
    return True


def _directed_neighbor_switch(G, w, unsat, h_node_residual_out, chords,
                              h_partition_in, partition):
    """ directed_neighbor_switch  releases one free stub for node w, while
        preserving joint degree.
        First, it selects node w_prime that (1) has the same degree as w and
        (2) is unsaturated. Then, it selects node v, a neighbor of w, that is
        not connected to w_prime and does an edge swap i.e. removes (w,v) and
        adds (w_prime,v). If neighbor switch is not possible for w using
        w_prime and v, then return w_prime; in [1] it's proven that
        such unsaturated nodes can be used.

    Parameters
    ----------
    G : networkx directed graph
        graph within which the edge swap will take place.
    w : integer
        node id for which we need to perform a neighbor switch.
    unsat: set of integers
        set of node ids that have the same degree as w and are unsaturated.
    h_node_residual_out: dict of integers
        for a given node, keeps track of the remaining stubs to be added.
    chords: set of tuples
        keeps track of available positions to add edges.
    h_partition_in: dict of integers
        for a given node, keeps track of its partition id (in degree).
    partition: integer
        partition id to check if chords have to be updated.

    References
    ----------
    [1] B. Tillman, A. Markopoulou, C. T. Butts & M. Gjoka,
        "Construction of Directed 2K Graphs". In Proc. of KDD 2017.
    """
    w_prime = unsat.pop()
    unsat.add(w_prime)
    # select node t, a neighbor of w, that is not connected to w_prime
    w_neighbs = list(G.successors(w))
    # slightly faster declaring this variable
    w_prime_neighbs = list(G.successors(w_prime))

    for v in w_neighbs:
        if (v not in w_prime_neighbs) and w_prime != v:
            # removes (w,v), add (w_prime,v)  and update data structures
            G.remove_edge(w, v)
            G.add_edge(w_prime, v)

            if h_partition_in[v] == partition:
                chords.add((w, v))
                chords.discard((w_prime, v))

            h_node_residual_out[w] += 1
            h_node_residual_out[w_prime] -= 1
            if h_node_residual_out[w_prime] == 0:
                unsat.remove(w_prime)
            return None

    # If neighbor switch didn't work, use unsaturated node
    return w_prime


def _directed_neighbor_switch_rev(G, w, unsat, h_node_residual_in, chords,
                                  h_partition_out, partition):
    """ directed_neighbor_switch_rev is similar to directed_neighbor_switch
        except it handles this operation for incoming edges instead of
        outgoing.

    Parameters
    ----------
    G : networkx directed graph
        graph within which the edge swap will take place.
    w : integer
        node id for which we need to perform a neighbor switch.
    unsat: set of integers
        set of node ids that have the same degree as w and are unsaturated.
    h_node_residual_in: dict of integers
        for a given node, keeps track of the remaining stubs to be added.
    chords: set of tuples
        keeps track of available positions to add edges.
    h_partition_out: dict of integers
        for a given node, keeps track of its partition id (out degree).
    partition: integer
        partition id to check if chords have to be updated.
    """
    w_prime = unsat.pop()
    unsat.add(w_prime)
    # slightly faster declaring these as variables.
    w_neighbs = list(G.predecessors(w))
    w_prime_neighbs = list(G.predecessors(w_prime))
    # select node v, a neighbor of w, that is not connected to w_prime.
    for v in w_neighbs:
        if (v not in w_prime_neighbs) and w_prime != v:
            # removes (v,w), add (v,w_prime) and update data structures.
            G.remove_edge(v, w)
            G.add_edge(v, w_prime)
            if h_partition_out[v] == partition:
                chords.add((v, w))
                chords.discard((v, w_prime))

            h_node_residual_in[w] += 1
            h_node_residual_in[w_prime] -= 1
            if h_node_residual_in[w_prime] == 0:
                unsat.remove(w_prime)
            return None

    # If neighbor switch didn't work, use the unsaturated node.
    return w_prime


@py_random_state(3)
def directed_joint_degree_graph(in_degrees, out_degrees, nkk, seed=None):
    """ Return a random simple directed graph with the given degree sequence
        (degree_seq), joint degree dictionary (nkk).

    Parameters
    ----------
    degree_seq :  list of tuples (of size 3)
        degree sequence contains tuples of nodes with node id, in degree and
        out degree.
    nkk  :  dictionary of dictionary of integers
        directed joint degree dictionary, for nodes of out degree k (first
        level of dict) and nodes of in degree l (second level of dict)
        describes the number of edges.
    seed : hashable object, optional
        Seed for random number generator.

    Returns
    -------
    G : Graph
        A directed graph with the specified inputs.

    Raises
    ------
    NetworkXError
        If degree_seq and nkk are not realizable as a simple directed graph.


    Notes
    -----
    Similarly to the undirected version:
    In each iteration of the "while loop" the algorithm picks two disconnected
    nodes v and w, of degree k and l correspondingly,  for which nkk[k][l] has
    not reached its target yet i.e. (for given k,l): n_edges_add < nkk[k][l].
    It then adds edge (v,w) and always increases the number of edges in graph G
    by one.

    The intelligence of the algorithm lies in the fact that  it is always
    possible to add an edge between disconnected nodes v and w, for which
    nkk[degree(v)][degree(w)] has not reached its target, even if one or both
    nodes do not have free stubs. If either node v or w does not have a free
    stub, we perform a "neighbor switch", an edge rewiring move that releases a
    free stub while keeping nkk the same.

    The difference for the directed version lies in the fact that neighbor
    switches might not be able to rewire, but in these cases unsaturated nodes
    can be reassigned to use instead, see [1] for detailed description and
    proofs.

    The algorithm continues for E (number of edges in the graph) iterations of
    the "while loop", at which point all entries of the given nkk[k][l] have
    reached their target values and the construction is complete.

    References
    ----------
    [1] B. Tillman, A. Markopoulou, C. T. Butts & M. Gjoka,
        "Construction of Directed 2K Graphs". In Proc. of KDD 2017.

    Examples
    --------
    >>> import networkx as nx
    >>> in_degrees = [0, 1, 1, 2]
    >>> out_degrees = [1, 1, 1, 1]
    >>> nkk = {1:{1:2,2:2}}
    >>> G=nx.directed_joint_degree_graph(in_degrees, out_degrees, nkk)
    >>>
    """
    if not is_valid_directed_joint_degree(in_degrees, out_degrees, nkk):
        msg = 'Input is not realizable as a simple graph'
        raise nx.NetworkXError(msg)

    # start with an empty directed graph.
    G = nx.DiGraph()

    # for a given group, keep the list of all node ids.
    h_degree_nodelist_in = {}
    h_degree_nodelist_out = {}
    # for a given group, keep the list of all unsaturated node ids.
    h_degree_nodelist_in_unsat = {}
    h_degree_nodelist_out_unsat = {}
    # for a given node, keep track of the remaining stubs to be added.
    h_node_residual_out = {}
    h_node_residual_in = {}
    # for a given node, keep track of the partition id.
    h_partition_out = {}
    h_partition_in = {}
    # keep track of non-chords between pairs of partition ids.
    non_chords = {}

    # populate data structures
    for idx, i in enumerate(in_degrees):
        idx = int(idx)
        if i > 0:
            h_degree_nodelist_in.setdefault(i, [])
            h_degree_nodelist_in_unsat.setdefault(i, set())
            h_degree_nodelist_in[i].append(idx)
            h_degree_nodelist_in_unsat[i].add(idx)
            h_node_residual_in[idx] = i
            h_partition_in[idx] = i

    for idx, o in enumerate(out_degrees):
        o = out_degrees[idx]
        non_chords[(o, in_degrees[idx])] = non_chords.get((o, in_degrees[idx]),
                                                          0) + 1
        idx = int(idx)
        if o > 0:
            h_degree_nodelist_out.setdefault(o, [])
            h_degree_nodelist_out_unsat.setdefault(o, set())
            h_degree_nodelist_out[o].append(idx)
            h_degree_nodelist_out_unsat[o].add(idx)
            h_node_residual_out[idx] = o
            h_partition_out[idx] = o

        G.add_node(idx)

    nk_in = {}
    nk_out = {}
    for p in h_degree_nodelist_in:
        nk_in[p] = len(h_degree_nodelist_in[p])
    for p in h_degree_nodelist_out:
        nk_out[p] = len(h_degree_nodelist_out[p])

    # iterate over every degree pair (k,l) and add the number of edges given
    # for each pair.
    for k in nkk:
        for l in nkk[k]:
            n_edges_add = nkk[k][l]

            if (n_edges_add > 0):
                # chords contains a random set of potential edges.
                chords = set()

                k_len = nk_out[k]
                l_len = nk_in[l]
                chords_sample = seed.sample(range(k_len * l_len), n_edges_add
                                            + non_chords.get((k, l), 0))

                num = 0
                while len(chords) < n_edges_add:
                    i = h_degree_nodelist_out[k][chords_sample[num] % k_len]
                    j = h_degree_nodelist_in[l][chords_sample[num] // k_len]
                    num += 1
                    if i != j:
                        chords.add((i, j))

                # k_unsat and l_unsat consist of nodes of in/out degree k and l
                # that are unsaturated i.e. those nodes that have at least one
                # available stub
                k_unsat = h_degree_nodelist_out_unsat[k]
                l_unsat = h_degree_nodelist_in_unsat[l]

                while n_edges_add > 0:
                    v, w = chords.pop()
                    chords.add((v, w))

                    # if node v has no free stubs then do neighbor switch.
                    if h_node_residual_out[v] == 0:
                        _v = _directed_neighbor_switch(G, v, k_unsat,
                                                       h_node_residual_out,
                                                       chords, h_partition_in,
                                                       l)
                        if _v is not None:
                            v = _v

                    # if node w has no free stubs then do neighbor switch.
                    if h_node_residual_in[w] == 0:
                        _w = _directed_neighbor_switch_rev(G, w, l_unsat,
                                                           h_node_residual_in,
                                                           chords,
                                                           h_partition_out, k)
                        if _w is not None:
                            w = _w

                    # add edge (v,w) and update data structures.
                    G.add_edge(v, w)
                    h_node_residual_out[v] -= 1
                    h_node_residual_in[w] -= 1
                    n_edges_add -= 1
                    chords.discard((v, w))

                    if h_node_residual_out[v] == 0:
                        k_unsat.discard(v)
                    if h_node_residual_in[w] == 0:
                        l_unsat.discard(w)
    return G
