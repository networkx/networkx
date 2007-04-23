#!/usr/bin/env python
"""
An example using networkx.XGraph(multiedges=True).

Calculate the Kevin Bacon numbers of some actors.  The data in
kevin_bacon.dat is a subset from all movies with Kevin Bacon in
the cast, as taken from the example in the Boost Graph Library.
cf. http://www.boost.org/libs/graph/doc/kevin_bacon.html

"""
__author__ = """Pieter Swart (swart@lanl.gov)"""
__date__ = "$Date: 2005-04-13 16:16:18 -0600 (Wed, 13 Apr 2005) $"
__credits__ = """"""
__revision__ = ""

#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from networkx import *

def kevin_bacon_graph():
    """Return the graph of actors connected by a movie.

    Uses data from kevin_bacon.dat from Boost Graph Library.
    Each edge between two actors contain the movie name.
    
    """
    # open file miles.dat.gz (or miles.dat)
    try:
        try:
            import gzip
            datafile=gzip.open('kevin_bacon.dat.gz','r')
        except:
            datafile=open("kevin_bacon.dat","r")
    except IOError:
        raise "File kevin_bacon.dat not found."

    G=XGraph(multiedges=True)

    for line in datafile.read().splitlines():
        actor1, movie, actor2 = line.split(';')
        G.add_edge(actor1, actor2, movie)
    return G

if __name__ == '__main__':
    from networkx import *

    G=kevin_bacon_graph()
    print "Loaded the kevin_bacon_graph from kevin_bacon.dat"
    print "Graph has %d actors with %d edges"\
          %(number_of_nodes(G),number_of_edges(G))
    
    bacon_no={}
    for a in G:
        bacon_no[a]=shortest_path_length(G,a,'Kevin Bacon')

    for a in G:
        print "%s's bacon number is %d" %(a,bacon_no[a])

    try:
        # draw using graphviz interface
        # node size = 50*degree
        # node color corresponds to bacon number
        import pylab as P
        draw_graphviz(G,prog='fdp',
                      with_labels=False,
                      node_size=[50*G.degree(n) for n in G],
                      node_color=P.array([bacon_no[n] for n in G]),
                      cmap=P.cm.gray
                      )
        P.savefig("kevin_bacon.png")
        print "created kevin_bacon.png"
    except:
        pass
