#!/usr/bin/env python
"""
An example using networkx.XGraph().

miles_graph() returns an undirected graph over the 128 US cities from
the datafile miles_dat.txt. The cities each have location and population
data.  The edges are labeled with the distance betwen the two cities.

This example is described in Section 1.1 in Knuth's book [1,2].

References.
-----------

[1] Donald E. Knuth,
    "The Stanford GraphBase: A Platform for Combinatorial Computing",
    ACM Press, New York, 1993.
[2] http://www-cs-faculty.stanford.edu/~knuth/sgb.html


"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import networkx as NX


def miles_graph():
    """ Return the cites example graph in miles_dat.txt
        from the Stanford GraphBase.
    """
    # open file miles_dat.txt.gz (or miles_dat.txt)
    try:
        try:
            import gzip
            fh = gzip.open('miles_dat.txt.gz','r')
        except:
            fh=open("miles_dat.txt","r")
    except IOError:
        raise "File miles_dat.txt not found."

    G=NX.XGraph()
    G.position={}
    G.population={}

    cities=[]
    for line in fh.readlines():
        if line.startswith("*"): # skip comments
            continue

        numfind=re.compile("^\d+") 

        if numfind.match(line): # this line is distances
            dist=line.split()
            for d in dist:
                G.add_edge(city,cities[i],int(d))
                i=i+1
        else: # this line is a city, position, population
            i=1
            (city,coordpop)=line.split("[")
            cities.insert(0,city)
            (coord,pop)=coordpop.split("]")
            (y,x)=coord.split(",")
        
            G.add_node(city)
            # assign position - flip x axis for matplotlib, shift origin
            G.position[city]=(-int(x)+7500,int(y)-3000)
            G.population[city]=float(pop)/1000.0
    return G            

if __name__ == '__main__':
    import networkx as NX
    import re
    import sys

    G=miles_graph()

    print "Loaded miles_dat.txt containing 128 cities."
    print "digraph has %d nodes with %d edges"\
          %(NX.number_of_nodes(G),NX.number_of_edges(G))


    # make new graph of cites, edge if less then 300 miles between them
    H=NX.Graph()
    for v in G:
        H.add_node(v)
    for (u,v,d) in G.edges():
        if d < 300:
            H.add_edge(u,v)

    # draw with matplotlib/pylab            

    try:
        import pylab as P
        # with nodes sized py population
#        draw(H,G.position,
#             node_size=[G.population[v] for v in H],
#             with_labels=False)
        # with nodes colored by degree sized by population
        node_color=P.array([float(H.degree(v)) for v in H])
        NX.draw(H,G.position,
             node_size=[G.population[v] for v in H],
             node_color=node_color,
             with_labels=False)
        P.savefig("miles.png")
    except:
        pass



