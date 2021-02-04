import networkx as nx
from typing import Callable, Tuple
from tqdm.auto import tqdm
import numpy as np


def hill_climb_optimize(G, R, modify_graph, n_iter):
    """
    Optimize graph for a rewiring rule encapsulated by `modify_graph` through
    the hill climb metaheuristic.

    Arguments
    G: Graph to optimize
    R: Utility function
    n_iter: Max number of temperature drops
    """
    return simulated_annealing_optimize(G,
                                        R,
                                        modify_graph,
                                        n_iter=n_iter,
                                        T_max=np.infty,
                                        T_decay=0.0,
                                        max_no_improve=1
                                        )


def simulated_annealing_optimize(G: nx.Graph,
                                 R: Callable[[nx.Graph], float],
                                 modify_graph: Callable[[nx.Graph], nx.Graph],
                                 n_iter: int = 3000,
                                 T_max: float = 300,
                                 T_decay: float = 0.1,
                                 max_no_improve: int = 10) -> Tuple[float, nx.Graph]:
    """
    Optimize graph for a rewiring rule encapsulated by `modify_graph` through
    the simulated annealing metaheuristic.

    Arguments
    G: Graph to optimize
    R: Utility function
    n_iter: Max number of temperature drops
    T_max: Initial temperature (above zero)
    T_decay: Decay on each temperature drop (between 0 and 1)
    max_no_improve: How much inner iterations on each annealing step (above 0)
    """
    # Initial checks
    if T_max <= 0:
        raise ValueError('T_max should be a floating number above zero')
    if T_decay < 0 or T_decay > 1:
        raise ValueError('T_decay should be between 0.0 and 1.0')
    if max_no_improve < 1:
        raise ValueError('max_no_improve should be above 1')

    # Set initial state 
    G_temp = G.copy()
    T = T_max
    R_last = R(G_temp)

    # Temperature drop loop
    for _ in tqdm(range(n_iter)):
        no_improve = 0
        R_new = R_last

        # Iterate on the same temperature until we don't have more improvements
        # bounded by max_no_improve.
        while no_improve < max_no_improve:
          
            # Try to rewire edge
            G_attempt = modify_graph(G_temp.copy())
            R_attempt = R(G_attempt)

            # Try to perform a local optimization
            delta_R = R_attempt - R_new
            if delta_R > 0:
                temp_G = G_attempt
                R_new = R_attempt
            else:
                # Accept a worse attempt with a given probability
                y = np.random.rand()  # Unif[0, 1]
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
                no_improve += 1

        # Drop temperature
        T = T * (1 - T_decay)

    return (R_last, G_temp)