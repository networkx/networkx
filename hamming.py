def hamming_distance(G1, G2):
    '''
    This Function calculates the Hamming Distance for two potentially directed graphs.
    '''
    import numpy as np

    for node in G1.nodes():
        if node not in G2.nodes():
            G2.add_node(node)

    for node in G2.nodes():
        if node not in G1.nodes():
            G1.add_node(node)

    A1=np.array(nx.to_numpy_matrix(G1))
    A2=np.array(nx.to_numpy_matrix(G2))

    return sum(ch1!=ch2 for ch1, ch2 in zip(list(A1.flatten()), list(A2.flatten())))
