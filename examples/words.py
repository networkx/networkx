"""
The words.dat example from the Stanford Graph Base.

SGBWords() returns an undirected graph over the 5757 5-letter
words in the datafile words.dat.  Two words are connected by an edge
if they differ in one letter, resulting in 14,135 edges. This example
is described in Section 1.1 in Knuth's book [1,2].

References.
----------

[1] Donald E. Knuth,
    "The Stanford GraphBase: A Platform for Combinatorial Computing",
    ACM Press, New York, 1993.
[2] http://www-cs-faculty.stanford.edu/~knuth/sgb.html

"""

__author__ = """Brendt Wohlberg\nAric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-04-01 07:56:04 -0700 (Fri, 01 Apr 2005) $"
__credits__ = """"""
__revision__ = ""
#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from NX import *
import re
import sys

__author__ = """"""
__date__ = ""
__credits__ = """"""
__version__ = ""
# $Header$


#-------------------------------------------------------------------
#   The Words/Ladder graph of Section 1.1
#-------------------------------------------------------------------

def _notComment(line):
    return not(line.startswith('*'))


def _wdist(a,b):
    """ Return simple edit distance between two words a and b. """

    d=abs(len(a)-len(b))
    for k in range(0,min(len(a),len(b))):
        if a[k] != b[k]:
            d = d + 1
    return d


def words_graph():
    """ Return the words example graph from the Stanford GraphBase"""

    datafile = 'words.dat'
    words = map(lambda x: x[0:5], filter(_notComment, open(datafile).readlines()))
    if not words:   # zero length
        raise StandardError, "error reading graph definition data in ", datafile

    G = Graph(name="words")

    for w in words:
        G.add_node(w)
    for k in xrange(0,len(words)):
        for l in xrange(k+1,len(words)):
            if _wdist(words[k],words[l]) == 1:
                G.add_edge(words[k],words[l])
    
    return G




if __name__ == '__main__':
    from NX import *
    print "Loading words.dat"
    G=words_graph()
    print "Loaded Donald Knuth's words.dat containing 5757 five-letter English words."
    print "Two words are connected if they differ in one letter."
    print "graph has %d nodes with %d edges"\
          %(number_of_nodes(G),number_of_edges(G))

    sp=shortest_path(G, 'chaos', 'order')
    print "shortest path between 'chaos' and 'order' is:\n", sp

    sp=shortest_path(G, 'nodes', 'graph')
    print "shortest path between 'nodes' and 'graph' is:\n", sp

    sp=shortest_path(G, 'pound', 'marks')
    print "shortest path between 'pound' and 'marks' is:\n", sp

    print number_connected_components(G),"connected components"

    
