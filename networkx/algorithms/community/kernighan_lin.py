from collections import defaultdict
from operator import itemgetter
import random
import networkx as nx
#    Copyright(C) 2011 by
#    Ben Edwards <bedwards@cs.unm.edu>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__="""\n""".join(['Ben Edwards (bedwards@cs.unm.edu)',
                          'Aric Hagberg (hagberg@lanl.gov)'])

def _compute_delta(G,A,B,weight):
    # helper to compute initial swap deltas for a pass
    delta = defaultdict(float)
    for u,v,d in G.edges(data=True):
        w = d.get(weight,1)
        if u in A:
            if v in A:
                delta[u] -= w
                delta[v] -= w
            elif v in B:
                delta[u] += w
                delta[v] += w
        elif u in B:
            if v in A:
                delta[u] += w
                delta[v] += w
            elif v in B:
                delta[u] -= w
                delta[v] -= w
    return delta

def _update_delta(delta,G,A,B,u,v,weight):
    # helper to update swap deltas during single pass
    for _,nbr,d in G.edges(u,data=True):
        w = d.get(weight,1)
        if nbr in A:
            delta[nbr] += 2*w
        if nbr in B:
            delta[nbr] -= 2*w
    for _,nbr,d in G.edges(v,data=True):
        w = d.get(weight,1)
        if nbr in A:
            delta[nbr] -= 2*w
        if nbr in B:
            delta[nbr] += 2*w
    return delta

def _kernighan_lin_pass(G, A, B, weight):
    # do a single iteration of Kernighan-Lin algorithm 
    # returns list of  (g_i,u_i,v_i) for i node pairs u_i,v_i
    multigraph = G.is_multigraph()
    delta = _compute_delta(G,A,B,weight)
    swapped = set()
    gains = []
    while len(swapped) < len(G):
        gain = []
        for u in A-swapped:
            for v in B-swapped:
                try:
                    if multigraph:
                        w = sum(d.get(weight,1) for k,d in G[u][v].items())
                    else:
                        w = G[u][v].get(weight,1)
                except KeyError:
                    w = 0
                gain.append((delta[u] + delta[v] -2 * w, u, v)) 
        if len(gain) == 0:
            break
        maxg,u,v = max(gain,key=itemgetter(0))
        swapped.update(set([u,v]))
        gains.append((maxg,u,v))
        delta = _update_delta(delta, G, A-swapped, B-swapped, u, v, weight)
    return gains        
    

def kernighan_lin_bisection(G, partition=None, max_iter=10, weight='weight'):
    """Partition G into two node sets using the Kernighan-Lin Algorithm.

    This algorithm paritions a network into two sets by iteratively
    swapping pairs of nodes to reduce the edge cut between the two sets.

    Parameters
    ----------
    G : graph
    partition : list (optional)
      List of two containers (e.g. sets) containing an intial partition.
      If not specified a random balanaced partition is used.
    max_iter : int
      Maximum number of times to attempt swaps
      to find an improvemement before giving up
    weight : key (default='weight')
      Edge data key to use as weight.  If None the weights are all set to 1.

    Returns
    -------
    partition : list of sets
      Partition of the nodes of the graph into two sets

    Raises
    -------
    NetworkXError
      if partition is not a valid partition of the graph into two communities

    Examples
    --------
    >>> G = nx.barbell_graph(3,0)
    >>> nx.kernighan_lin(G)

    Notes
    -----

    References
    ----------
    .. [1] Kernighan, B. W.; Lin, Shen (1970). 
       An efficient heuristic procedure for partitioning graphs. 
       Bell Systems Technical Journal 49: 291-307. Oxford University Press 2011.
    """
    if G.is_directed():
        raise NetworkXError('Not defined for directed graphs.')
    if partition is None:
        # split randomly into two balanced partitions
        nodes = G.nodes()
        random.shuffle(nodes)
        h = len(nodes)/2
        A,B = [set(nodes[:h]),set(nodes[h:])]
    else:
        try:
            # make a copy of partition as two sets
            A,B = set(partition[0]),set(partition[1]) 
        except:
            raise ValueError('partition must be two sets')
        if not nx.unique_community(G, [A,B]):
            raise nx.NetworkXError("partition invalid")
    i=0
    while i < max_iter:
        i+=1
        # gains is a list of  (g_i,u_i,v_i) for i node pairs u_i,v_i
        gains = _kernighan_lin_pass(G, A, B, weight)
        # cumulative sum of gains
        csum = list(nx.utils.cumulative_sum(c for c,u,v in gains))
        # index of max cumulative sum
        index = csum.index(max(csum))
        cgain = csum[index]
        if cgain <= 0:
            break
        # node pairs corresponding to gains[0],...,gains[index]
        anodes,bnodes = map(set,zip(*gains[:index+1])[1:3])
        A |= bnodes
        A -= anodes
        B |= anodes
        B -= bnodes
    return A,B
if __name__=='__main__':
    import networkx as nx
    import numpy as np
    import pylab
    # example from
    # http://users.eecs.northwestern.edu/~haizhou/357/lec2.pdf
    A = np.matrix([[0,  1,  2,  3,  2,  4],
                   [1,  0,  1,  4,  2,  1],
                   [2,  1,  0,  3,  2,  1],
                   [3,  4,  3,  0,  4,  3],
                   [2,  2,  2,  4,  0,  2],
                   [4,  1,  1,  3,  2,  0]])

    G=nx.from_numpy_matrix(A)
    G=nx.relabel_nodes(G,dict(enumerate('abcdef')))
    print(kernighan_lin_bisection(G,partition=[set(['a','b','c']),set(['d','e','f'])]))

    G=nx.barbell_graph(3,0)
    M = nx.MultiGraph(G)
    M.add_edge(2,3)
    M.add_edge(2,3)
#    M.add_edge(2,3)
    A,B=kernighan_lin_bisection(M)
    print(A,B)
    # G=nx.cycle_graph(50)
    # A,B=kernighan_lin_bisection2(G)
    # print A,B
    print(nx.cut_size(M,A,B))
    pos=nx.spring_layout(M)
    pylab.clf()
    nx.draw_networkx_nodes(G,pos,nodelist=A,node_color='r')
    nx.draw_networkx_nodes(G,pos,nodelist=B,node_color='b')
    nx.draw_networkx_labels(G,pos)
    nx.draw_networkx_edges(G,pos)
    pylab.draw()

