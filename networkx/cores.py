"""
Find and manipulate the k-cores of a graph

"""
__author__ = """Dan Schult(dschult@colgate.edu)"""
__date__ = "$Date: 2005-03-30 16:56:28 -0700 (Wed, 30 Mar 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 911 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

def find_cores(G,with_labels=True):
   """Return the core number for each vertex.

   See: arXiv:cs.DS/0310049 by Batagelj and Zaversnik

   If with_labels is True a dict is returned keyed by node to the core number. 
   If with_labels is False a list of the core numbers is returned.
   """
   # compute the degrees of each vertex
   degrees=G.degree(with_labels=True)
   
   # sort verticies by degree
   valuesfirst= [ [a[1],a[0]] for a in degrees.items() ]
   valuesfirst.sort()
   verts= [ vf[1] for vf in valuesfirst]  # vertices
   
   # Set up initial guesses for core and lists of neighbors.
   core= degrees
   nbrs={}
   for v in verts:
       nbrs[v]=G.neighbors(v)
   
   # form vertex core building up from smallest
   for v in verts:
       for u in nbrs[v]:
          if core[u] > core[v]:
             nbrs[u].remove(v)
             posu=verts.index(u)
             while core[verts[posu]]==core[u]:
                 posu -= 1
             verts.remove(u)
             verts.insert(posu+1,u)
             core[u] -= 1
   if with_labels:
      return core
   else:
      return core.values()


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('../tests/cores.txt',package='networkx')
    return suite

if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    


