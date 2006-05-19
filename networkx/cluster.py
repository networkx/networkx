"""
Compute clustering coefficients and transitivity of graphs.

Clustering coefficient  
  For each node find the fraction of possible triangles that are triangles,
  c_i = triangles_i / (k_i*(k_i-1)/2)
  where k_i is the degree of node i.       

  A coefficient for the whole graph is the average C = avg(c_i)

Transitivity 
  Find the fraction of all possible triangles which are in fact triangles.
  Possible triangles are identified by the number of "triads" (two edges
  with a shared vertex)

  T = 3*triangles/triads

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
__date__ = "$Date: 2005-06-14 12:48:10 -0600 (Tue, 14 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1012 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

def triangles(G,nbunch=None,with_labels=False):
    """ Return number of triangles for nbunch of nodes.
        If nbunch is None, then return triangles for every node.
        If with_labels is True, return a dict keyed by node.
    
        Note: Each triangle is counted three times: once at each vertex.
    """
    G_has_edge=G.has_edge # cache function

    if nbunch is None: # include all nodes via iterator
        nbunch=G.nodes_iter()
    elif nbunch in G: # if nbunch is a node, return one value
        v_nbrs=G.neighbors(nbunch)
        triangles= [ u for u in v_nbrs for w in v_nbrs if G_has_edge(u,w) ]
        ntriangles=len(triangles)
        if with_labels:
            return {nbunch:ntriangles/2} # useless but consistent?
        else:
            return ntriangles/2
    # handle bunch of nodes
    tri={}
    for v in nbunch:
        v_nbrs=G.neighbors(v)
        triangles= [ u for u in v_nbrs for w in v_nbrs if G_has_edge(u,w) ]
        ntriangles=len(triangles)
        tri[v]=ntriangles/2
             
    if with_labels:
        return tri
    else:
        if len(tri)==1: return tri.values()[0] # return single value
        return tri.values()

def average_clustering(G):
    """ Average clustering coefficient for a graph.

        Note: this is a space saving routine; It might be faster
        to use clustering to get a list and then take average.
    """
    order=G.order()
    s=sum(clustering(G))
    return s/float(order)

def clustering(G,nbunch=None,with_labels=False,weights=False):
    """ 
    Clustering coefficient for each node in nbunch.

    If with_labels is True, return a dict keyed by node.

    If both with_labels and weights are True, return both 
    a clustering coefficient dict keyed by node and a
    dict of weights based on degree.  The weights are
    the fraction of connected triples in the graph which
    include the keyed node.  Ths is useful in moving from
    transitivity for clustering coefficient and back.
    """
    if nbunch is None: # include all nodes via iterator
        nbunch=G.nodes_iter()
    # if nbunch is a node then convert into list
    elif nbunch in G:
        nbunch=[nbunch]

    clusterc={}
    for (v,deg) in G.degree_iter(nbunch, with_labels=True):
        if deg <= 1:    # isolated vertex or single pair gets cc 0
            clusterc[v]=0.0
        else:
            ntriangles=triangles(G,v)
            max_n=(deg*(deg-1))/2
            clusterc[v]=float(ntriangles)/float(max_n)

    if with_labels:
        if weights:
            degree=G.degree(with_labels=True)
            # scale by one over twice the number of triples
            scale=1./sum([ deg*(deg-1) for deg in degree.itervalues() ]) 
            weight={}
            for v in clusterc:
                deg=degree[v]
                weight[v]=deg*(deg-1)*scale   # also twice, but cancels in scaling
            return clusterc,weight
        else:
            return clusterc
    else:
        if len(clusterc)==1: return clusterc.values()[0] # return single value
        return clusterc.values()

def transitivity(G):
    """ Transitivity (fraction of transitive triangles) for a graph"""
    G_has_edge=G.has_edge # cache function

    triangles=0 # 6 times number of triangles
    contri=0  # 2 times number of connected triples
    for v in G.nodes_iter():
        v_nbrs=G.neighbors(v)
        deg=len(v_nbrs)
        contri += deg*(deg-1)
        triangles += len([ u for u in v_nbrs for w in v_nbrs if G_has_edge(u,w) ])
    return float(triangles)/float(contri)


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/cluster.txt',package='networkx')
    return suite

if __name__ == "__main__":
    import os
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
    

