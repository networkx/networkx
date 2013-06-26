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
