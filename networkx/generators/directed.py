"""
Generators for some directed graphs.

gn_graph: growing network 
gnc_graph: growing network with copying
gnr_graph: growing network with redirection
scal_

"""
#    Copyright (C) 2006-2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
__author__ ="""Aric Hagberg (hagberg@lanl.gov)\nWillem Ligtenberg (W.P.A.Ligtenberg@tue.nl)"""

__all__ = ['gn_graph', 'gnc_graph', 'gnr_graph','scale_free_graph']

import math
import random

import networkx
from networkx.generators.classic import empty_graph, cycle_graph
from networkx import MultiDiGraph
from networkx.utils import discrete_sequence


def gn_graph(n,kernel=lambda x:x ,seed=None):
    """Return the GN (growing network) digraph with n nodes.

    The graph is built by adding nodes one at a time with a link
    to one previously added node.  The target node for the link is chosen
    with probability based on degree.  The default attachment kernel is
    a linear function of degree.

    The graph is always a (directed) tree.

    Example:

    >>> D=nx.gn_graph(10)       # the GN graph
    >>> G=D.to_undirected()  # the undirected version

    To specify an attachment kernel use the kernel keyword

    >>> D=nx.gn_graph(10,kernel=lambda x:x**1.5) # A_k=k^1.5

    Reference::

      @article{krapivsky-2001-organization,
      title   = {Organization of Growing Random Networks},
      author  = {P. L. Krapivsky and S. Redner},
      journal = {Phys. Rev. E},
      volume  = {63},
      pages   = {066123},
      year    = {2001},
      }


    """
    G=empty_graph(1,create_using=networkx.DiGraph())
    G.name="gn_graph(%s)"%(n)

    if seed is not None:
        random.seed(seed)

    if n==1:
        return G

    G.add_edge(1,0) # get started
    ds=[1,1] # degree sequence

    for source in range(2,n):
        # compute distribution from kernel and degree
        dist=[kernel(d) for d in ds] 
        # choose target from discrete distribution 
        target=discrete_sequence(1,distribution=dist)[0]
        G.add_edge(source,target)
        ds.append(1)  # the source has only one link (degree one)
        ds[target]+=1 # add one to the target link degree
    return G


def gnr_graph(n,p,seed=None):
    """Return the GNR (growing network with redirection) digraph with n nodes
    and redirection probability p.

    The graph is built by adding nodes one at a time with a link
    to one previously added node.  The previous target node is chosen
    uniformly at random.  With probabiliy p the link is instead "redirected"
    to the successor node of the target.  The graph is always a (directed)
    tree.

    Example:

    >>> D=nx.gnr_graph(10,0.5)  # the GNR graph
    >>> G=D.to_undirected()  # the undirected version

    Reference::

      @article{krapivsky-2001-organization,
      title   = {Organization of Growing Random Networks},
      author  = {P. L. Krapivsky and S. Redner},
      journal = {Phys. Rev. E},
      volume  = {63},
      pages   = {066123},
      year    = {2001},
      }

    """
    G=empty_graph(1,create_using=networkx.DiGraph())
    G.name="gnr_graph(%s,%s)"%(n,p)

    if not seed is None:
        random.seed(seed)

    if n==1:
        return G

    for source in range(1,n):
        target=random.randrange(0,source)
        if random.random() < p and target !=0:
            target=G.successors(target)[0]
        G.add_edge(source,target)

    return G



def gnc_graph(n,seed=None):
    """Return the GNC (growing network with copying) digraph with n nodes.

    The graph is built by adding nodes one at a time with a links
    to one previously added node (chosen uniformly at random)
    and to all of that node's successors.

    Reference::

      @article{krapivsky-2005-network,
      title   = {Network Growth by Copying},
      author  = {P. L. Krapivsky and S. Redner},
      journal = {Phys. Rev. E},
      volume  = {71},
      pages   = {036118},
      year    = {2005},
      }

    """
    G=empty_graph(1,create_using=networkx.DiGraph())
    G.name="gnc_graph(%s)"%(n)

    if not seed is None:
        random.seed(seed)

    if n==1:
        return G

    for source in range(1,n):
        target=random.randrange(0,source)
        for succ in G.successors(target):
            G.add_edge(source,succ)
        G.add_edge(source,target)

    return G


def scale_free_graph(n, G=None,
                     alpha=0.41,
                     beta=0.54,
                     gamma=0.05,
                     delta_in=0.2,
                     delta_out=0,
                     seed=None):
    """Return a scale free directed graph

    Parameters
    ----------
    n : integer
       Number of nodes in graph

    G : NetworkX graph (optional)
       Use as starting graph in algorithm

    alpha : float 
       Probability for adding a new node conecgted to an existing node
       chosen randomly according to the in-degree distribution.

    beta : float
       Probability for adding an edge between two existing nodes.
       One existing node is chosen randomly according the in-degree 
       distribution and the other chosen randomly according to the out-degree 
       distribution.
       
    gamma : float
       Probability for adding a new node conecgted to an existing node
       chosen randomly according to the out-degree distribution.
        
    delta_in : float
       Bias for choosing ndoes from in-degree distribution.

    delta_out : float
       Bias for choosing ndoes from out-degree distribution.

    delta_out : float
       Bias for choosing ndoes from out-degree distribution.

    seed : integer (optional)
       Seed for random number generator

    Examples
    --------
    >>> G=nx.scale_free_graph(100)

    
    Notes
    -----
    The sum of alpha, beta, and gamma must be 1.

    Algorithm from
    
    @article{bollobas2003dsf,
    title={{Directed scale-free graphs}},
    author={Bollob{\'a}s, B. and Borgs, C. and Chayes, J. and Riordan, O.},
    journal={Proceedings of the fourteenth annual ACM-SIAM symposium on Discrete algorithms},
    pages={132--139},
    year={2003},
    publisher={Society for Industrial and Applied Mathematics Philadelphia, PA, USA}
    }

"""

    def _choose_node(G,distribution,delta):
        cumsum=0.0
        # normalization 
        psum=float(sum(distribution.values()))+float(delta)*len(distribution)
        r=random.random()
        for i in range(0,len(distribution)):
            cumsum+=(distribution[i]+delta)/psum
            if r < cumsum:  
                break
        return i

    if G is None:
        # start with 3-cycle
        G=MultiDiGraph()
        G.add_edges_from([(0,1),(1,2),(2,0)])

    if alpha <= 0:
        raise ValueError('alpha must be >= 0.')
    if beta <= 0:
        raise ValueError('beta must be >= 0.')
    if gamma <= 0:
        raise ValueError('beta must be >= 0.')

    if alpha+beta+gamma !=1.0:
        raise ValueError('alpha+beta+gamma must equal 1.')
        
    G.name="directed_scale_free_graph(%s,alpha=%s,beta=%s,gamma=%s,delta_in=%s,delta_out=%s)"%(n,alpha,beta,gamma,delta_in,delta_out)

    # seed random number generated (uses None as default)
    random.seed(seed)

    while len(G)<n:
        r = random.random()
        # random choice in alpha,beta,gamma ranges
        if r<alpha:
            # alpha
            # add new node v
            v = len(G) 
            # choose w according to in-degree and delta_in
            w = _choose_node(G, G.in_degree(with_labels=True),delta_in)
        elif r < alpha+beta:
            # beta
            # choose v according to out-degree and delta_out
            v = _choose_node(G, G.out_degree(with_labels=True),delta_out)
            # choose w according to in-degree and delta_in
            w = _choose_node(G, G.in_degree(with_labels=True),delta_in)
        else:
            # gamma
            # choose v according to out-degree and delta_out
            v = _choose_node(G, G.out_degree(with_labels=True),delta_out)
            # add new node w
            w = len(G) 
        G.add_edge(v,w)
        
    return G

