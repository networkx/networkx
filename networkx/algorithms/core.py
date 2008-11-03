"""
Find and manipulate the k-cores of a graph

"""
__author__ = """Dan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
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
   verts= [node for deg,node in sorted( (d,n) for n,d in degrees.iteritems() )]
   
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

