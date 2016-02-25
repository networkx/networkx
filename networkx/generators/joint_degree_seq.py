"""Generate graphs with a given joint degree 
"""
#    BSD license.
import random

import networkx as nx

__author__ = "\n".join(['Minas Gjoka <minas.gjoka@gmail.com>'])

__all__ = ['is_valid_joint_degree',
           'joint_degree_model']


def is_valid_joint_degree(nkk):
    """ Checks whether the given joint degree dictionary (nkk) is realizable 
        as a simple graph by evaluating five necessary and sufficient conditions.
        
    Here is the list of five conditions that an input nkk needs to satisfy for
    simple graph realizability:
    - Condition    1:  nkk[k][l]  is integer for all k,l    
    - Condition    2:  sum(nkk[k])/k = number of nodes with degree k, is an integer    
    - Conditions 3,4: number of edges between k and l cannot exceed maximum possible number of edges 
    - Condition    5: nkk[k][k] is an even integer i.e. stubs are counted twice for equal degree pairs.
                      this is an assumption that the method joint_degree_model expects to be true.
           

    Parameters
    ----------
    nkk :  dictionary of dictionary of integers
        joint degree dictionary. for nodes of degree k (first level of dict) and
        nodes of degree l (second level of dict) describes the number of edges        
    
    
    Returns
    -------
    boolean
        returns true if given joint degree dictionary is realizable, else returns false.

    
    References
    ----------
    [1] M. Gjoka, M. Kurant, A. Markopoulou, "2.5K Graphs: from Sampling to Generation",
    IEEE Infocom, 2013.
    
    """
    
            
    nk = {}
    for k in nkk:
        if k>0:
            k_size = float( sum(val for val in nkk[k].itervalues()) ) / float( k )
            if not k_size.is_integer():  # condition 2
                return False
            nk[k] = k_size
            
            
    for k in nkk:
        for l in nkk[k]:
            if not float(nkk[k][l]).is_integer(): # condition 1 
                return False            
            
            if (k!=l) and ( nkk[k][l] > nk[k]*nk[l] ): #condition 3
                return False
            elif (k==l): 
                if ( nkk[k][k] > nk[k]*(nk[k]-1) ): # condition 4
                    return False
                if (nkk[k][k] % 2 != 0): # condition 5
                    return False                
    
        
    # if all five above conditions have been satisfied then the input nkk is 
    # realizable as a simple graph.            
    return True

def _neighbor_switch(G, w, unsat, h_node_residual, avoid_node_id=None):    
    """ neighbor_switch  releases one free stub for node w, while preserving joint degree. 
    First, it selects node w_prime that (1) has the same degree as w and (2) is unsaturated.
    Then, it selects node t, a neighbor of w, that is not connected to w_prime and does 
    an edge swap i.e. removes (w,t) and adds (w_prime,t). Gjoka et. al. [1] prove that if 
    (1) and (2) are true then such an edge swap is always possible.     
        

    Parameters
    ----------
    G : networkx undirected graph 
        graph within which the edge swap will take place
    w : integer
        node id for which we need to perform a neighbor switch 
    unsat: set of integers
        set of node ids that have the same degree as w and are unsaturated
    h_node_residual: dict of integers
        for a given node, keeps track of the remaining stubs to be added.
    avoid_node_id: integer
        node id to avoid when selecting w_prime. only used for a rare edge case.
    
    
    References
    ----------
    [1] M. Gjoka, B. Tillman, A. Markopoulou, "Construction of Simple Graphs 
       with a Target Joint Degree Matrix and Beyond", IEEE Infocom, 2015.
    
    """
    
    if avoid_node_id==None or h_node_residual[avoid_node_id]>1:
        # select node w_prime that has the same degree as w and is unsatured        
        w_prime = next(iter(unsat))
    else:
        # assume that inside method joint_degree_model the node pair (v,w) is a candidate
        # for connection (v=avoid_node_id). if neighbor_switch is called for node w inside method 
        # joint_degree_model and (1) candidate nodes v=avoid_node_id and w have the same degree i.e.
        # degree(v)=degree(w) and (2) node v=avoid_node_id is a potential candidate for w_prime
        # but has only  one stub left i.e. h_node_residual[v]==1, then prevent v from
        # being selected as w_prime. This is a rare edge case.
        
        iter_var  = iter(unsat)
        while True:
            w_prime = next(iter_var)
            if w_prime != avoid_node_id:
                break
        
    # select node t, a neighbor of w, that is not connected to w_prime
    w_prime_neighbs = G[w_prime] # slightly faster declaring this variable
    for v in G[w]: 
        if (v not in w_prime_neighbs) and (v!=w_prime):
            t = v
            break;
    
    # removes (w,t), add (w_prime,t)  and update data structures
    G.remove_edge(w, t)
    G.add_edge(w_prime, t)
    h_node_residual[w] += 1                            
    h_node_residual[w_prime] -= 1                        
    if h_node_residual[w_prime] == 0:
        unsat.remove(w_prime)

        
def joint_degree_model(nkk,seed=None):
    """Return a random simple graph with the given joint degree dict (nkk).

    Parameters
    ----------
    nkk :  dictionary of dictionary of integers
        joint degree dictionary. for nodes of degree k (first level of dict) and
        nodes of degree l (second level of dict) describes the number of edges        
    seed : hashable object, optional
        Seed for random number generator.

    Returns
    -------
    G : Graph
        A graph with the specified joint degree dict

    Raises
    ------
    NetworkXError
        If nkk, the joint degree dictionary, is not realizable.


    Notes
    -----
    In each iteration of the "while loop" the algorithm picks two disconnected nodes v and w,
    of degree k and l correspondingly,  for which nkk[k][l] has not reached its target yet 
    i.e. (for given k,l): n_edges_add < nkk[k][] . It then adds edge (v,w) and always increases
    the number of edges in graph G by one.  
    
    The intelligence of the algorithm lies in the fact that  it is always  possible 
    to add an edge between disconnected nodes v and w, for which nkk[degree(v)][degree(w)] 
    has not reached its target, even if one or both nodes do not have free stubs. If either node 
    v or w   does not have a free stub, we perform a "neighbor switch", an edge rewiring move that 
    releases a free stub while keeping nkk the same.
    
    The algorithm continues for E (number of edges in the graph) iterations of the "while loop",
    at the which point all entries of the given nkk[k][l] have reached their
    target values and the construction is complete.        

    References
    ----------
    [1] M. Gjoka, B. Tillman, A. Markopoulou, "Construction of Simple Graphs 
       with a Target Joint Degree Matrix and Beyond", IEEE Infocom, 2015.

    Examples
    --------
    >>> import networkx as nx
    >>> joint_degree_dict = {1: {4: 1},
                             2: {2: 2, 3: 2, 4: 2},
                             3: {2: 2, 4: 1},
                             4: {1: 1, 2: 2, 3: 1}}
    >>> G=nx.joint_degree_model(joint_degree_dict)
    >>>

    """
    
    if not is_valid_joint_degree(nkk):
        msg = 'Input joint degree dict not realizable as a simple graph'
        raise nx.NetworkXError(msg)

    if not seed is None:
        random.seed(seed)

    # compute degree vector from joint degree nkk
    nk = { deg:(sum(val for val in nkk[deg].itervalues())/deg) for deg in nkk if deg>0 }
    
    # start with empty N-node graph
    N = int(sum(deg for deg in nk.itervalues()))
    G = nx.empty_graph(N)
    
    
    # for a given degree group, keep the list of all node ids 
    h_degree_nodelist = {}
    
    # for a given node, keep track of the remaining stubs to be added. 
    h_node_residual = {}
    
    # populate h_degree_nodelist and h_node_residual
    nodeid = 0    
    for degree, numNodes in nk.iteritems(): 
        h_degree_nodelist[degree] = range(nodeid, nodeid+int(numNodes))         
        for v in h_degree_nodelist[degree]:
            h_node_residual[v] = degree  
        nodeid += int(numNodes)
                                        
    # iterate over every degree pair (k,l) and add the number of edges given for each pair
    for k in nkk:
        for l in nkk[k]:
            
            # n_edges_add is the number of edges to add for the degree pair (k,l) 
            n_edges_add = nkk[k][l] 
            
            if (n_edges_add>0) and (k>=l):                                                                 

                # number of nodes with degree k and l
                k_size = nk[k]
                l_size = nk[l]    
                
                # k_nodes and l_nodes consist of all nodes of degree k and l respectivelyu                
                k_nodes = h_degree_nodelist[k]
                l_nodes = h_degree_nodelist[l]

                # k_unsat and l_unsat consist of nodes of degree k and l that are unsaturated
                # i.e. those nodes that have at least one available stub
                k_unsat = set(v for v in k_nodes if h_node_residual[v]>0)                        
                
                if k!=l:
                    l_unsat = set(w for w in l_nodes if h_node_residual[w]>0) 
                else:
                    l_unsat = k_unsat
                    n_edges_add = nkk[k][l]/2
                    
                while n_edges_add > 0:
                    
                    # randomly pick nodes v and w that have degrees k and l
                    v = k_nodes[ random.randint(0,k_size-1) ]
                    w = l_nodes[ random.randint(0,l_size-1) ]
    
                    # if nodes v and w are disconnected then attempt to connect
                    if not G.has_edge(v,w) and (v!=w): 
                        
                        # if node v has no free stubs then do neighbor switch
                        if h_node_residual[v]==0:                         
                            _neighbor_switch(G, v, k_unsat, h_node_residual)    
                            
                        # if node w has no free stubs then do neighbor switch
                        if h_node_residual[w]==0:                      
                            if k!=l:
                                _neighbor_switch(G, w, l_unsat, h_node_residual)                
                            else:
                                _neighbor_switch(G, w, l_unsat, h_node_residual, avoid_node_id=v)                
                            
                        # add edge (v,w) and update data structures
                        G.add_edge(v,w)  
                        h_node_residual[v] -= 1
                        h_node_residual[w] -= 1   
                        n_edges_add -= 1     
                            
                        if h_node_residual[v] == 0:
                            k_unsat.discard(v)
                        if h_node_residual[w] == 0:
                            l_unsat.discard(w)                      
                                        
            
    G.name="joint_degree_model %d nodes"%(G.order())    
    return G

