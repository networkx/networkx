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

def generalized_hd(G, H, no_edge_cost=0.5):
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

def diversity(obj_set, distance=generalized_hd):
    '''
    This function calculates the Weitzman diversity measure (Weitzman 1992) of a set of objects with a distance function defined over any
    two objects in the set.
    '''
    S=set()
    divers=0
    g=obj_set.pop() #Step1: randomly pick an object from the object set
    S.add(g)
    while obj_set:
        set_distance=min([distance(g, h) for g in S for h in obj_set])
        min_elem=[elem for elem in obj_set if min([distance(elem, g) for g in S])==set_distance].pop()

        S.add(min_elem) #Step2: add closest member of the object set to the set, S
        obj_set.remove(min_elem) #and remove it from the object set
        divers+=set_distance #Step3: increment the diversity by the distance between the set S, and the new member.

    #Normalize the diversity by the number of objects:
    return float(divers)/len(S)
