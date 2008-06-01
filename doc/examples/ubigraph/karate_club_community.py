#!/usr/bin/env python
"""
Communities in Zachary's Karate Club graph.

Double-click to expand and contract communities.

Data file from:
http://vlado.fmf.uni-lj.si/pub/networks/data/Ucinet/UciData.htm

Reference:
Zachary W. (1977).
An information flow model for conflict and fission in small groups.
Journal of Anthropological Research, 33, 452-473.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\n Katy Bold (kbold@princeton.edu"""
#    Copyright (C) 2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import string

def karate_graph(create_using=None, **kwds):
    from networkx.generators.classic import empty_graph

    G=empty_graph(34,create_using=create_using,**kwds)
    G.name="Zachary's Karate Club"

    zacharydat="""\
0 1 1 1 1 1 1 1 1 0 1 1 1 1 0 0 0 1 0 1 0 1 0 0 0 0 0 0 0 0 0 1 0 0
1 0 1 1 0 0 0 1 0 0 0 0 0 1 0 0 0 1 0 1 0 1 0 0 0 0 0 0 0 0 1 0 0 0
1 1 0 1 0 0 0 1 1 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 1 0
1 1 1 0 0 0 0 1 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 1
0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
1 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1
0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1
1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1
1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 0 1 0 0 1 1
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 0 0 0 1 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 1 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1
0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 1
0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 0 1 1
0 1 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1
1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 1 0 0 0 1 1
0 0 1 0 0 0 0 0 1 0 0 0 0 0 1 1 0 0 1 0 1 0 1 1 0 0 0 0 0 1 1 1 0 1
0 0 0 0 0 0 0 0 1 1 0 0 0 1 1 1 0 0 1 1 1 0 1 1 0 0 1 1 1 1 1 1 1 0"""


    row=0
    for line in string.split(zacharydat,'\n'):
        thisrow=map(int,string.split(line,' '))
        for col in range(0,len(thisrow)):
            if thisrow[col]==1:
                G.add_edge(row,col) # col goes from 0,33
        row+=1
    return G

def contract_community(G,K,community):
    G.add_node(community['label'],color=community['color'],size='2.0')
    for node in community['nodes']:
        for nbr in G.neighbors(node):
            if nbr not in community['nodes']:
                G.add_edge(community['label'],nbr)
        G.delete_node(node)


def expand_community(G,K,community):
    G.delete_node(community['label'])
    for node in community['nodes']:
        G.add_node(node,color=community['color'])
    for node in community['nodes']:
        for nbr in K.neighbors(node):
            if nbr in G:
                G.add_edge(node,nbr)
            else:
                G.add_edge(node,node_map[nbr])


def get_communities():
    # assign communities and some properties
    communities={}
    communities['c1']={}
    communities['c2']={}
    communities['c3']={}
    communities['c4']={}
    communities['c1']['nodes']=[0, 1, 2, 3, 7, 11, 12, 13, 17, 19, 21]
    communities['c2']['nodes']=[4, 5, 6, 10, 16]
    communities['c3']['nodes']=[8, 9, 14, 15, 18, 20, 22, 26, 29, 30, 32, 33]
    communities['c4']['nodes']=[23, 24, 25, 27, 28, 31]
    communities['c1']['color']='#ff0000'
    communities['c2']['color']='#00ff00'
    communities['c3']['color']='#0000ff'
    communities['c4']['color']='#afafaf'
    communities['c1']['label']='c1'
    communities['c2']['label']='c2'
    communities['c3']['label']='c3'
    communities['c4']['label']='c4'

    node_map={}
    for label,c in communities.items():
        for n in c['nodes']:
            node_map[n]=label
    return communities,node_map


def vertex_callback(id):
    import sys
    try:
        n=G.idnode[id]
        if n in node_map:
            contract_community(G,K,communities[node_map[n]])
        elif n in communities:
            expand_community(G,K,communities[n])
    except:
        return -1
    return 0



if __name__ == "__main__":
    import random
    import networkx as nx
    K=karate_graph()
    G=nx.UbiGraph(K)
    G.node_labels()
    communities,node_map=get_communities()
    for key,c in communities.items():
        G.set_node_attr(c['nodes'],color=c['color'])


    print "Double-click to expand and contract communities."

    # call back server        
    myPort = random.randint(20739,20999)
    # Set up a callback for left double-clicks on vertices.
    G.ubigraph.set_vertex_style_attribute(0, "callback_left_doubleclick", 
                "http://127.0.0.1:" + str(myPort) + "/vertex_callback")

    # Now make an XMLRPC server to handle tha callbacks.
    from SimpleXMLRPCServer import SimpleXMLRPCServer
    # Create server
    server = SimpleXMLRPCServer(("localhost", myPort))
    server.register_introspection_functions()
    server.register_function(vertex_callback)
    # Run the server's main loop
    print "Listening for callbacks from ubigraph_server on port " + str(myPort)
    server.serve_forever()
