# Functions to get the segmentation of the graph
# g correspond to the graph, k is the set of voronoi nodes or breaking nodes, z is a variable that define wheter the segmentation
# is done considering the inward edges or the outward egdes of each voronoi node.
# 0: for undirected graphs; It means it doesn't matter the direction of edges
# 1: makes the segementation considering outward edges
# 2: makes the segmentation considering inward edges.

def parallel_dijkstra(g, k, z):

    nbors = type_ident(g, z)

    nx.set_node_attributes(g, 'Dv', 1000)
    nx.set_node_attributes(g, 'V', 'N')
    nx.set_node_attributes(g, 'visit', 0)

    i = 0                    # Identify the Voronoi Nodes
    Q = []
    tag = []
    while i < len(k):
        if k[i] in g:
            g.node[k[i]]['Dv'] = 0
            g.node[k[i]]['V'] = 'V'+str(i)
            tag.append('V'+str(i))
            heapq.heappush(Q, (0, k[i]))
            i += 1

    # Node Expansion: First find the lowest value and check not visited node
    while len(Q) != 0:
        v = heapq.heappop(Q)
        g.node[v[1]]['visit'] = 1        # Mark the node as visited

        # Visit all the neighbors of the node to be expanded
        for nbr in nbors(v[1]):
            if g.node[nbr]['visit'] == 0:
                if z == 2:
                    delta = g.node[v[1]]['Dv'] + (g.get_edge_data(nbr, v[1]))['weight']
                else:
                    delta = g.node[v[1]]['Dv'] + (g.get_edge_data(v[1], nbr))['weight']

                if g.node[nbr]['Dv'] == 1000:
                    g.node[nbr]['Dv'] = delta
                    g.node[nbr]['V'] = g.node[v[1]]['V']
                    heapq.heappush(Q, (delta, nbr))

                if (g.node[nbr]['Dv'] < 1000) and (delta < g.node[nbr]['Dv']):
                    g.node[nbr]['V'] = g.node[v[1]]['V']
                    g.node[nbr]['Dv'] = delta
    return g, tag


def type_ident(g, t):
    ginfo = nx.info(g)
    ginfo = ginfo.split('\n')
    ginfo = ginfo[1].split(':')

    if ginfo[1] == ' Graph':
        n_obj = g.neighbors
    elif t == 1:
        n_obj = g.neighbors
    elif t == 2:
        n_obj = g.predecessors
    else:
        n_obj = g.neighbors

    return n_obj
    
