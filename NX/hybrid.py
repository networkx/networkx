"""
Hybrid 

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
__date__ = "$Date: 2005-03-30 16:56:28 -0700 (Wed, 30 Mar 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 911 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import copy
import sets
from NX import shortest_path

def kl_connected_subgraph(G,k,l,**kwds):
    """ Returns the maximum locally (k,l) connected subgraph of G.

        (k,l)-connected subgraphs are presented by Fan Chung and Li
        in "The Small World Phenomenon in hybrid power law graphs"
        to appear in "Complex Networks" (Ed. E. Ben-Naim) Lecture
        Notes in Physics, Springer (2004)

        low_memory=True then use a slightly slower, but  lower memory version
        same_as_graph=True then return a tuple with subgraph and
        pflag for if G is kl-connected
    """
    lowmem=kwds.get('low_memory',False)
    same_as_graph=kwds.get('same_as_graph',False)
    H=copy.deepcopy(G)    # subgraph we construct by removing from G
    
    graphOK=True
    deleted_some=True # hack to start off the while loop
    while deleted_some:
        deleted_some=False
        for edge in H.edges():
            (u,v)=edge
            ### Get copy of graph needed for this search
            if lowmem:
                verts=sets.Set([u,v])
                for i in range(k):
                    [verts.update(G.neighbors(w)) for w in verts.copy()]
                G2=G.subgraph(list(verts))
            else:
                G2=copy.deepcopy(G)
            ###
            path=[u,v]
            cnt=0
            accept=0
            while path:
                cnt += 1 # Found a path
                if cnt>=l:
                    accept=1
                    break
                # record edges along this graph
                prev=u
                for w in path:
                    G2.delete_edge(prev,w)
                    prev=w
                path=shortest_path(G2,u,v,k)  # ??? should "Cutoff" be k+1?
            # No Other Paths
            if accept==0:
                H.delete_edge(u,v)
                deleted_some=True
                if graphOK: graphOK=False
    # We looked through all edges and removed none of them.
    # So, H is the maximal (k,l)-connected subgraph of G
    if same_as_graph:
        return (H,graphOK)
    return H

def is_kl_connected(G,k,l,**kwds):
    """Returns True if G is kl connected """
    lowmem=kwds.get('low_memory',False)
    graphOK=True
    for edge in G.edges():
        (u,v)=edge
        ### Get copy of graph needed for this search
        if lowmem:
            verts=sets.Set([u,v])
            for i in range(k):
                [verts.update(G.neighbors(w)) for w in verts.copy()]
            G2=G.subgraph(list(verts))
        else:
            G2=copy.deepcopy(G)
        ###
        path=[u,v]
        cnt=0
        accept=0
        while path:
            cnt += 1 # Found a path
            if cnt>=l:
                accept=1
                break
            # record edges along this graph
            prev=u
            for w in path:
                G2.delete_edge(prev,w)
                prev=w
            path=shortest_path(G2,u,v,k)  # ??? should "Cutoff" be k+1?
        # No Other Paths
        if accept==0:
            graphOK=False
            break
    # return status
    return graphOK


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/hybrid.txt',package='NX')
    return suite


if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    
