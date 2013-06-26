def hamming_distance(G, H):
    '''
    This function computes the Hamming Distance between two (possibly directed) graphs;
    this improved version was suggested by Aric Hagberg.
    '''
    count = 0
    for e in G.edges_iter():
        if not H.has_edge(*e):
            count+=1
    for e in H.edges_iter():
        if not G.has_edge(*e):
            count+=1
    return count

def generalized_hd(G, H, no_edge_cost=0.5, max_relation=2):
    '''
    This function computes a generalized Hamming Distance, of a (possibly weighted and directed) graph, where not having a relation
    has a potentially different cost than having a zero relation
    '''
    count=0
    for e in G.edges_iter():
        if H.has_edge(*e):
            try: count+= abs(nx.get_edge_attributes(G, 'weight')[e]-nx.get_edge_attributes(H, 'weight')[e])
            except: print '%s does not have a weight!' % str(e)
        else:
            try: count+= (abs(nx.get_edge_attributes(G, 'weight')[e]) + no_edge_cost)
            except: print '%s does not have a weight!' % str(e)

    #And now for the edges that are in H but not in G:
    for e in H.edges_iter():
        if not G.has_edge(*e):
            try: count+= (abs(nx.get_edge_attributes(H, 'weight')[e]) + no_edge_cost)
            except: print '%s does not have a weight!' % str(e)

    return count
