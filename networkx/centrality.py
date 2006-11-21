"""
Centrality measures.

"""
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)"""
__date__ = "$Date: 2005-07-06 08:02:28 -0600 (Wed, 06 Jul 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1064 $"

def betweenness_centrality(G,v=False,cutoff=False,normalized=True):
    """Betweenness centrality for nodes.
    The fraction of number of shortests paths that go
    through each node.

    Returns a dictionary of betweenness values keyed by node.
    The betweenness is normalized to be between [0,1].
    The algorithm is described in [brandes-2003-faster]_.

    If normalized=False the resulting betweenness is not normalized.

    Reference:

    .. [brandes-2003-faster] Ulrik Brandes,
       Faster Evaluation of Shortest-Path Based Centrality Indices, 2003,
       available at http://citeseer.nj.nec.com/brandes00faster.html
    
    """
    if v:   # only one node
        betweenness=0
        for source in G.nodes(): 
            ubetween=_node_betweenness(G,source,cutoff=cutoff,normalized=normalized )
            betweenness+=ubetween[v]
        return betweenness
    else:
        betweenness={}.fromkeys(G.nodes(),0) 
        for source in betweenness: 
            ubetween=_node_betweenness(G,source,cutoff=cutoff,normalized=False)
            for vk in ubetween:
                betweenness[vk]+=ubetween[vk]
        if normalized:
            order=len(betweenness)
            scale=1.0/((order-1)*(order-2))
            for v in betweenness:
                betweenness[v] *= scale
        return betweenness  # all nodes

def _node_betweenness(G,source,cutoff=False,normalized=True):
    """See betweenness_centrality for what you probably want.

    This is betweenness for a single node.
    The fraction of number of shortests paths from source that go
    through each node.

    To get the betweenness for a node you need to do all-pairs
    shortest paths.  

    """
    # get the predecessor and path length data
    (pred,length)=_fast_predecessor(G,source,cutoff) 

    # order the nodes by path length
    onodes = [ (l,vert) for (vert,l) in length.items() ]
    onodes.sort()
    onodes[:] = [vert for (l,vert) in onodes]
    
    # intialize betweenness
    between={}.fromkeys(length,1.0)
    # work through all paths
    # remove source
    while onodes:           
        v=onodes.pop()
        if (pred.has_key(v)):
            num_paths=len(pred[v])   # Discount betweenness if more than 
            for x in pred[v]:        # one shortest path.
                if x==source:        # stop if hit source because all remaining v  
                    break            #  also have pred[v]==[source]
                between[x]+=between[v]/num_paths
    for v in between:
        between[v]-=1
    # rescale to be between 0 and 1                
    if normalized:
        l=len(between)
        if l > 2:
            scale=1.0/float((l-1)*(l-2)) # 1/the number of possible paths
            for v in between:
                between[v] *= scale
    return between

def edge_betweenness(G,nodes=False,cutoff=False):
    """
    Edge Betweenness 

    WARNING:

    This module is for demonstration and testing purposes.

    """
    betweenness={} 
    if not nodes:         # find betweenness for every node  in graph
        nodes=G.nodes()   # that probably is what you want...
    for source in nodes: 
        ubetween=_edge_betweenness(G,source,nodes,cutoff=cutoff)
        for v in ubetween.keys():
            b=betweenness.setdefault(v,0)  # get or set default
            betweenness[v]=ubetween[v]+b    # cumulative total
    return betweenness

def _edge_betweenness(G,source,nodes,cutoff=False):
    """
    Edge betweenness helper.
    """
    between={}
    # get the predecessor data
    (pred,length)=_fast_predecessor(G,source,cutoff) 
    # order the nodes by path length
    onodes = map(lambda k: (length[k], k), length.keys())
    onodes.sort()
    onodes[:] = [val for (key, val) in onodes]
    # intialize betweenness
    [between.setdefault((u,v),1.0) for (u,v) in G.edges(nodes)] 
    [between.setdefault((v,u),1.0) for (u,v) in G.edges(nodes)] 
#    print between
    while onodes:           # work through all paths
        v=onodes.pop()
        if (pred.has_key(v)):
            num_paths=len(pred[v])   # Discount betweenness if more than 
            for w in pred[v]:        # one shortest path.
                if (pred.has_key(w)):
                    num_paths=len(pred[w])  # Discount betweenness, mult path  
                    for x in pred[w]: 
                        between[(w,x)]+=between[(v,w)]/num_paths
                        between[(x,w)]+=between[(w,v)]/num_paths
    return between



def _fast_predecessor(G,source,target=False,cutoff=False):
    """
    Helper for betweenness.

    Returns dict of predecessors and shortest path lengths.
    Cutoff is a limit on the number of hops traversed.
    """
    level=0                  # the current level
    nextlevel=[source]       # list of nodes to check at next level
    seen={source:level}      # level (number of hops) when seen in BFS
    pred={source:[]}         # predecessor hash
    while nextlevel:
        level=level+1
        thislevel=nextlevel
        nextlevel=[]
        for v in thislevel:
            for w in G.neighbors(v):
                if (not seen.has_key(w)): 
                    pred[w]=[v]
                    seen[w]=level
                    nextlevel.append(w)
                elif (seen[w]==level):# add v to predecessor list if it 
                    pred[w].append(v) # is at the correct level
        if (cutoff and cutoff <= level):
            break

    if target:
        if not pred.has_key(target): return ([],-1)  # No predecessor
        return (pred[target],seen[target])
    else:
        return (pred,seen) 

def degree_centrality(G,v=False):
    """
    Degree centrality for nodes (fraction of nodes connected to).

    Returns a dictionary of degree centrality values keyed by node.

    The degree centrality is normalized to be between 0 and 1.

    """
    degree_centrality={}
    deg=G.degree(with_labels=True)
    s=1.0/(G.order()-1.0)
    for vk in deg:
        degree_centrality[vk]=deg[vk]*s

    if not v:
        return degree_centrality
    else:
        return degree_centrality[v]

def closeness_centrality(G,v=False):
    """
    Closeness centrality for nodes (1/average distance to all nodes).

    Returns a dictionary of closeness centrality values keyed by node.
    The closeness centrality is normalized to be between 0 and 1.

    """
    from networkx.path import single_source_shortest_path_length

    closeness_centrality={}

    for n in G.nodes():
        sp=single_source_shortest_path_length(G,n)
        if sum(sp.values()) > 0.0:                                            
            s=(len(sp)-1.0)  # normalize to number of nodes-1 in connected part
            closeness_centrality[n]=s/sum(sp.values())                     
        else:                                                                
            closeness_centrality[n]=0.0           
    if not v:
        return closeness_centrality
    else:
        return closeness_centrality[v]


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/centrality.txt',package='networkx')
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
    
