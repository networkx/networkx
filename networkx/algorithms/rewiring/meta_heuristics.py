import networkx as nx
from typing import Callable, Tuple
import math
import random


def hill_climb_optimize(G: nx.Graph,
                        R: Callable[[nx.Graph], float],
                        modify_graph: Callable[[nx.Graph], nx.Graph],
                        n_iter=100):
    """
    Optimize graph through a rewiring rule by using a
    hill climbing metaheuristic.


    Parameters
    ----------
    G : NetworkX Graph
    R : Function
        Utility function that takes a graph and returns a float
    modify_graph : Function
        Rewiring function that takes a graph and returns a graph
    n_iter : int
        Max number of temperature drops


    Returns
    ----------
    R_temp : float
        R value of the optimized graph
    G_temp : NetworkX Graph
        Graph optimized through the Simulated Annealing algorithm + params


    References
    ----------
    James Paterson, Beatrice Ombuki-Berman (2020).
    A Hybrid Approach to Network Robustness Optimization using Edge Rewiring and Edge Addition
    2020 IEEE International Conference on Systems, Man, and Cybernetics (SMC), Toronto, ON, 2020, pp. 4051-4057
    doi: 10.1109/SMC42975.2020.9283269.
    """

    # Set initial state
    G_last = G.copy()
    R_last = R(G_last)

    # Monte Carlo Loop
    for _ in range(n_iter):
        # Try to rewire edge
        G_attempt = modify_graph(G_last.copy())
        R_attempt = R(G_attempt)

        # Try to perform a local optimization
        delta_R = R_attempt - R_last
        if delta_R > 0:
            R_last = R_attempt
            G_last = G_attempt

    return (R_last, G_last)


def simulated_annealing_optimize(
    G: nx.Graph,
    R: Callable[[nx.Graph], float],
    modify_graph: Callable[[nx.Graph], nx.Graph],
    n_iter: int = 3000,
    T_max: float = 300,
    T_decay: float = 0.1,
    max_no_improve: int = 10,
) -> Tuple[float, nx.Graph]:
    """
    Optimize graph through a rewiring rule by using a
    simulated annealing metaheuristic.


    Parameters
    ----------
    G : NetworkX Graph
    R : Function
        Utility function that takes a graph and returns a float
    modify_graph : Function
        Rewiring function that takes a graph and returns a graph
    n_iter : int
        Max number of temperature drops
    T_max : float
        Initial temperature (above zero)
    T_decay : flota
        Decay on each temperature drop (between 0 and 1)
    max_no_improve : int
        How much inner iterations on each annealing step (above 0)


    Returns
    ----------
    R_temp : float
        R value of the optimized graph
    G_temp : NetworkX Graph
        Graph optimized through the Simulated Annealing algorithm + params


    References
    ----------
    James Paterson, Beatrice Ombuki-Berman (2020).
    A Hybrid Approach to Network Robustness Optimization using Edge Rewiring and Edge Addition
    2020 IEEE International Conference on Systems, Man, and Cybernetics (SMC), Toronto, ON, 2020, pp. 4051-4057
    doi: 10.1109/SMC42975.2020.9283269.

    """
    # Initial checks
    if T_max <= 0:
        raise ValueError("T_max should be a floating number above zero")
    if T_decay < 0 or T_decay > 1:
        raise ValueError("T_decay should be between 0.0 and 1.0")
    if max_no_improve < 1:
        raise ValueError("max_no_improve should be above 1")

    # Set initial state
    G_temp = G.copy()
    T = T_max
    R_last = R(G_temp)

    # Temperature drop loop
    for _ in range(n_iter):
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
                y = random.random()  # Unif[0, 1]
                value = math.exp(-delta_R / T)
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
