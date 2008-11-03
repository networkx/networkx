"""
Generators for some directed graphs.

gn_graph: growing network 
gnc_graph: growing network with copying
gnr_graph: growing network with redirection

"""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
__author__ ="""Aric Hagberg (hagberg@lanl.gov)"""

__all__ = ['gn_graph', 'gnc_graph', 'gnr_graph']

import math
import random

import networkx
from networkx.generators.classic import empty_graph
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

