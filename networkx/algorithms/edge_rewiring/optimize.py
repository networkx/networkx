import networkx as nx
from typing import Callable, Tuple
from tqdm.auto import tqdm
import random
import numpy as np 

def sa_optimize(G: nx.Graph,
                R: Callable[[nx.Graph], float],
                n_iter=3000,
                T_max=300,
                T_decay=0.1,
                max_no_improve=10) -> Tuple[float, nx.Graph]:
    """

    Arguments
    G: Graph to optimize
    R: Utility function
    n_iter: Max number of temperature drops
    T_max: initial temperature
    T_decay: drops in temperature
    max_no_improve: 

    Reference: 
    """
    temp_G = G.copy()
    T = T_max.copy()
    R_last = 0

    grant_set = {node 
                 for node, data
                 in temp_G.nodes
                 if data['type'] == 'grant'}

    contributor_set = {node 
                       for node, data
                       in temp_G.nodes
                       if data['type'] == 'contributor'}

    for _ in tqdm(range(n_iter)):      
        no_improve = 0
        R_new = 0
        
        while no_improve > max_no_improve:

            # Try to rewire edge
            ## Select edge at random
            G_attempt = temp_G.copy()
            # Returns a random (src, dst) tuple
            random_edge, data = random.choice(temp_G.edges(data=True))

            ## Get random contributor & grant
            random_contributor = random.choice(contributor_set)
            random_grant = random.choice(grant_set)

            ## Rewire edges
            G_attempt.add_edge(random_contributor, random_grant, data)
            G_attempt.remove_edge(random_edge)
            R_attempt = R(G_attempt)

            # Try to perform a local optimization
            if R_attempt > R_new:
                temp_G = G_attempt
            else:
                y = np.random.rand() # Unif[0, 1]
                delta_R = R_attempt - R_new
                value = np.exp(-delta_R / T)
                if y < value:
                    temp_G = G_attempt
                    R_new = R_attempt
                else:
                    pass

            # Keep track of improvements
            if R_last < R_new:
                R_last = R_new
                no_improve = 0
            else:
                no_improve +=1

        # Drop temperature
        T = T * (1 - T_decay)

    return (R_last, temp_G)