import itertools
import math
import networkx as nx
import random
#    Copyright(C) 2011 by
#    Ben Edwards <bedwards@cs.unm.edu>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__="""\n""".join(['Ben Edwards (bedwards@cs.unm.edu)',
                          'Aric Hagberg (hagberg@lanl.gov)'])

try:
    from scipy.special import zeta as _zeta
except:
    def _zeta(alpha,x):
        z = 0.0
        z_prev = -1.0
        n = 0
        while z - z_prev > tol:
            z_prev = z
            z += 1.0/((xmin + n)**alpha)
            n+=1
        return z
    

""" not correct for fast version, either implement slow version or
figure out correct fast version
def random_block_model_graph(sizes, P, seed=None, directed=False):
    Return the random block model graph with a partition of sizes.

    A block model graph is a graph of communities with sizes defined by
    s in sizes. Nodes in community i and j are connected with probability
    P[i][j].

    Paramters
    ---------
    sizes : list of ints
      Sizes of groups
    P : list of list of floats
      probability of connecting a node in community i to a node in
      community j, with i,j in [0,len(sizes)-1]
    directed : boolean optional, default=False
      Whether to create a directed graph
    seed : int optional, default None
      A seed for the random number generator

    Returns
    -------
    G : NetworkX Graph or DiGraph
      random partition graph of size sum(gs)

    Raises
    ------
    NetworkXError
      Any P[i][j] is not in [0,1]
      If len(P) is not equal len(sizes)
      If len(P[i]) for all i is not equal
      to the len(sizes)

    Examples
    --------

    Notes
    -----
    This is a generalization of the random_partition_graph which allows
    different probabilities of connections between communities.
      
    References
    ----------
    
    # Use geometric method for O(n+m) complexity algorithm
    # partition=nx.community_sets(nx.get_node_attributes(G,'affiliation'))
    if not seed is None:
        random.seed(seed)

    if not len(P) == len(sizes):
        raise nx.NetworkXError("len(P) does not match len(sizes)")

    for i in range(len(P)):
        if not len(P[i])==len(sizes):
            raise nx.NetworkXError("len(P[%i]) does not match len(sizes)"%i)
        for j in range(len(P[i])):
            if not 0 <= P[i][j] <= 1:
                raise nx.NetworkXError("P[%i][%i] not in [0,1]"%(i,j))

    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    n = sum(sizes)
    G.add_nodes_from(range(n))
    # start with len(sizes) groups of gnp random graphs with parameter P[i][i]
    # graphs are unioned together with node labels starting at
    # 0, sizes[0], sizes[0]+sizes[1], ...
    next_group = {} # maps node key (int) to first node in next group
    start = 0
    group = 0
    for n in sizes:
        edges = ((u+start,v+start) 
                 for u,v in 
                 nx.fast_gnp_random_graph(n, P[group][group], directed=directed).edges())
        G.add_edges_from(edges)
        next_group.update(dict.fromkeys(range(start,start+n),start+n))
        for u in range(start,start+n):
            G.node[u]['affiliation']=group
        group += 1
        start += n

    # connect each node in group randomly with the nodes not in group
    # use geometric method like fast_gnp_random_graph()

    n = len(G)
    if directed:
        for u in range(n):
            v = 0
            while v < n:
                lr = math.log(1.0 - random.random())
                i = G.node[u]['affiliation']
                j = G.node[v]['affiliation']
                lp = math.log(1.0 - P[i][j])
                v += int(lr/lp)
                # skip over nodes in the same group as v, including self loops
                if next_group.get(v,n)==next_group[u]:
                    v = next_group[u]
                if v < n:
                    G.add_edge(u,v)
                    v += 1
    else:
        for u in range(n-1):
            v = next_group[u] # start with next node not in this group
            while v < n:
                i = G.node[u]['affiliation']
                j = G.node[v]['affiliation']
                lp = math.log(1.0 - P[i][j])  
                lr = math.log(1.0 - random.random())
                v += int(lr/lp)
                if v < n:
                    G.add_edge(u,v)
                    v += 1
    return G
"""        

def LFR_benchmark_graph(n,
                        tau1,
                        tau2,
                        mu,
                        average_degree=None,
                        min_degree=None,
                        max_degree=None,
                        min_community=None,
                        max_community=None,
                        tol=1.0e-7,
                        max_iters=500,
                        seed=None):
    """Generate the LFR benchmark graph for community finding
    algorithm testing.

    This algorithm proceeds as follows:

    1) Find a degree sequence with power a power_law distribution,
       and minimum value min_degree, which has approximate average
       degree average_degree. This is accomplished by either:
          a) specifying min_degree and not the average degree.
          b) Specifying the average degree, in which case a suitable
             minimum degree will be found.
       max_degree can also be specified otherwise it will be set to
       n. Each node u will have mu*degree(u) out of community links
       and (1-mu)*degree(u) in community links.
    2) Generate community sizes according to a powerlaw with exponent
       tau2. If max_community an min_community are not specified
       they will be selected to be the min_degree and max_degree.
       Community sizes are generated until the sum of their sizes
       is equal to n.
    3) Each node will be randomly assigned a community with the
       condition that the community is large enough for the nodes
       in community degree((1-mu)*degree(u)). If a community grows
       too large a random node will be selected for reassignment
       to a new community, until all nodes have been assinged a
       community.
    4) Each node u then adds (1-mu)*degree(u) in community links
       and mu*degree(u) out of community links.

    Parameters
    ----------
    n : int
      Number of nodes
    tau1 : float > 1
      Power law exponent for degree distribution
    tau2 : float > 1
      Power law exponent for the size of communities
    average_degree : float
      Desired average degree
    min_degree : int
      Minimum degree
    max_degree : int, optional (default=n)
      Maximum degree
    min_community : int, optional (default=min_degree)
      Minimum community size
    max_community : iny, optional
      Maximum community size
    tol : float, optional (default=1.0e-7)
      tolerance to match average degree
    max_iters : int, optional (default=500)
      number of iterations to try to create
      community sizes, degree distribution,
      community affiliation
    seed : int, optional (default=None)
      A random integer value seed

    Returns
    -------
    G : NetworkXGraph
      the LFR benchmark graph
    C : list of sets
      the actual community structure of the graph

    Raises
    ------
    NetworkXError
      If tau1 or tau2 <= 1
      If mu is not in [0,1]
      If max_degree is not in (0,n]
      If neither average_degree or min_degree is not specified
      If both average degree or min_degree is specified
      If a suitable min_degree cannot be found
      If max_community > n
      If min_community < 0
      If a valid degree sequence cannot be created in max_iters
      If a valid set of community sizes cannot be created in max_iters
      If a valid community assignment cannot be created in 10*n*max_iters

      Examples
      --------
      >>> G,C = nx.LFR_benchmark_graph(1000,
      ...                              3,
      ...                              1.5,
      ...                              .1,
      ...                              average_degree=15,
      ...                              min_community=10,
      ...                              seed=42)
      >>> len(C)
      7

      Notes
      -----
      This algorithm differs slightly from the original way it was
      presented[1].
        1)  Rather than connecting the graph via a configuration
            model then rewiring to match the in community and out
            community degree, we do this wiring explicitly at the
            end, which should be equivalent.
        2)  In the code posted on the author's website [2] they
            calculate the random powerlaw distributed variables
            and their average using continuous approximations, we
            use the discrete distributions here as both degree
            and community size are discrete.

       Though the authors describe the algorithm as quite robust,
       testing during development indicates that a somewhat narrower
       parameter set is likely to successfully produce a graph.
       Some suggestions have been provided in the event of exceptions.
       Time benchmarks are somewhat similar to those provided 

       References
       ----------
       .. [1] 'Benchmark graphs for testing community detection algorithms',
              Andrea Lancichinetti, Santo Fortunato, and Filippo Radicchi,
              Phys. Rev. E 78, 046110 2008
       .. [2] http://santo.fortunato.googlepages.com/inthepress2
       """
    if not seed is None:
        random.seed(seed)
    if not tau1 > 1:
        raise nx.NetworkXError("tau1 must be > 1")
    if not tau2 > 1:
        raise nx.NetworkXError("tau2 must be > 2")
    if not 0 <= mu <= 1:
        raise nx.NetworkXError("mu must be in [0,1]")
        
    deg_seq = _powerlaw_degree_sequence(n,
                                        tau1,
                                        average_degree,
                                        min_degree,
                                        max_degree,
                                        tol=tol,
                                        max_iters=max_iters)

    comm_sizes = _powerlaw_community_sequence(n,
                                              tau2,
                                              deg_seq,
                                              min_size=min_community,
                                              max_size=max_community,
                                              max_iters=max_iters)

    return _LFR_benchmark_graph(deg_seq,
                                comm_sizes,
                                mu,
                                tol=tol,
                                max_iters=max_iters)

def _powerlaw_degree_sequence(n,
                              gamma,
                              average_degree=None,
                              min_degree=None,
                              max_degree=None,
                              seed=None,
                              tol=1.0e-7,
                              max_iters=500):

    if max_degree is None:
        max_degree = n
    elif not 0 < max_degree <=n:
        raise nx.NetworkXError("max_degree must be in (0,n]")

    if min_degree is None and average_degree is None:
        raise nx.NetworkXError("Must assign either min_degree or average_degree")
    elif not min_degree is None and not average_degree is None:
        raise nx.NetworkXError("Must assign either min_degree or average_degree, not both")
    if not seed is None:
        random.seed(seed)

    if min_degree is None and not average_degree is None:
        min_deg_top = max_degree
        min_deg_bot = 1
        min_deg_mid = (min_deg_top-min_deg_bot)/2.0 + min_deg_bot
        itrs=0
        mid_avg_deg = 0.0
        while abs(mid_avg_deg - average_degree) > tol:
            if itrs > max_iters:
                raise nx.NetworkXError("Could not match average_degree")
            mid_avg_deg = 0.0
            for x in range(int(min_deg_mid),max_degree+1):
                mid_avg_deg += (x**(-gamma+1.0))/_zeta(gamma,min_deg_mid)
            if mid_avg_deg > average_degree:
                min_deg_top = min_deg_mid
                min_deg_mid = (min_deg_top-min_deg_bot)/2.0 + min_deg_bot
            else:
                min_deg_bot = min_deg_mid
                min_deg_mid = (min_deg_top-min_deg_bot)/2.0 + min_deg_bot
            itrs += 1
        min_degree = int(min_deg_mid + .5)

    itrs = 0
    while True:
        if itrs > max_iters:
            raise nx.NetworkXError("Could not create Valid Degree Sequence")
        deg_seq = []
        while len(deg_seq) < n:
            temp_pl = nx.utils.zipf_rv(gamma,min_degree)
            if temp_pl <= max_degree:
                deg_seq.append(temp_pl)
        itrs += 1
        if sum(deg_seq) % 2 == 0:
            break
    # pick kmin, kmax
    # generate sequence
    # check to make sure it is divisible by two, doesn't have to be graphical  
    return deg_seq

def _powerlaw_community_sequence(n,
                                 beta,
                                 degree_sequence,
                                 min_size=None,
                                 max_size=None,
                                 seed=None,
                                 max_iters=500):
    if not seed is None:
        random.seed(seed)

    if min_size is None:
        min_size = min(degree_sequence)
    if max_size is None:
        max_size = max(degree_sequence)
    n = len(degree_sequence)
    itrs = 0
    while True:
        if itrs > max_iters:
            raise nx.NetworkXError("Could not create valid community sequence")
        comm_sizes = []
        while sum(comm_sizes) < n:
            temp_pl = nx.utils.zipf_rv(beta,min_size)
            if temp_pl <= max_size:
                comm_sizes.append(temp_pl)
            itrs+=1
        if sum(comm_sizes) ==n:
            break
    return comm_sizes


def _LFR_benchmark_graph(degree_sequence, community_sizes, mu,
                         tol=1.0e-7, max_iters=500, seed=None):
    if not seed is None:
        random.seed(seed)
    if not 0 <= mu <= 1:
        raise nx.NetworkXError("mu must be in [0,1]")

    # assign communities
    comm = [set() for _ in range(len(community_sizes))]
    n = len(degree_sequence)
    free = range(n)
    i = 0
    while free:
        v = free.pop()
        c = random.choice(range(len(community_sizes)))
        s = int(degree_sequence[v]*(1-mu) + .5)
        if s < community_sizes[c]: # add to this community
            comm[c].add(v)
        else: # put back on free list
            free.append(v)
        # if the community is too big, remove a node            
        if len(comm[c]) > community_sizes[c]:
            u = comm[c].pop()
            free.append(u)
        if i > 10*n*max_iters:
            raise nx.NetworkXError('Could not assign communities. '
                                   'Try increasing min_community')
        i += 1


    # build graph
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for c in comm:
        for u in c:
            while G.degree(u) < round(degree_sequence[u]*(1-mu)):
                v  = random.choice(list(c))
                G.add_edge(u,v)
            while G.degree(u) < degree_sequence[u]:
                v = random.choice(range(n))
                if not v in c:
                    G.add_edge(u,v)
    G.graph['partition'] = comm
    return G

if __name__ == '__main__':
    degree_seq = _powerlaw_degree_sequence(100,2.1,10)
    community_sizes = _powerlaw_community_sequence(100,2.1,degree_seq,min_size=20)
    G = _LFR_benchmark_graph(degree_seq, community_sizes,.1)
