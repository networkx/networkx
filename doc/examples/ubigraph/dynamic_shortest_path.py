#!/usr/bin/env python
"""
Dynamically draw shortest path in Watts-Stogatz small world graph using 
Ubigraph callbacks.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\n Katy Bold (kbold@princeton.edu"""
#    Copyright (C) 2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html


def vertex_callback(id):
    import sys
    global start
    try:
        if start is not None:
            s=nx.shortest_path(G,G.idnode[start],G.idnode[id])
            e=zip(s[0:-1],s[1:])
            epath=[(u,v,G.get_edge(u,v)) for u,v in e]
            print >> sys.stderr, s
            G.set_edge_attr(epath,style=wideyellow)
            start=None
        else:
            start=id
            G.set_edge_attr(style=gray)
    except:
        return -1
    return 0



if __name__ == "__main__":
    import random
    import networkx as nx

    print "double click nodes to find shortest path"
    G=nx.UbiGraph(nx.watts_strogatz_graph(50,4,0.1))
    G.node_labels() # turn on node labels
    G.set_edge_attr(color='#3f3f3f') # dark grey edges
    gray=G.new_edge_style(color='#3f3f3f',width='2.0')
    wideyellow=G.new_edge_style(color='#ffff00',width='6.0')

    start=None


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
