"""
Calculates the fitness function between two graphs.
"""

__all__ = ["fitness"]

import networkx as nx
import logging

LOGֹ_FORMAT = "%(levelname)s, time: %(asctime)s , line: %(lineno)d- %(message)s "
# create and configure logger
logging.basicConfig(filename='malicious_algo_logging.log', level=logging.DEBUG, filemode='w')
logger = logging.getLogger()


def fitness(sub_G1, sub_G2, G1_num_of_nodes, G1_num_of_edges, G2_num_of_nodes, G2_num_of_edges):
    """
    Measures the proportion of the number of different edges
    between two given graphs against the number of edges in the
    smaller graph, to evaluate a chromosome. That will be called the
    difference, noted by d, of the graphs. The difference value 0
    means that G2 is a complete subgraph of G1.
    The function returns the difference.

    Parameters
    ----------
    G1 = (V1, E1), G2 = (V2, E2), and |V1|≤|V2|.
    sub_G1 : NetworkX DiGraph
        sub_G1 is a dirceted subgraph of G1
    sub_G2 : NetworkX DiGraph
        sub_G2 is a dirceted subgraph of G2
    G1_num_of_nodes: int
        the number of nodes in the original graph (G1)
    G1_num_of_edges: int
        the number of edges in the original graph (G1)
    G2_num_of_nodes: int
        the number of nodes in the original graph (G2)
    G2_num_of_edges: int
        the number of edges in the original graph (G2)
    Note: |V1|≤|V2|.

    Returns
    -------
    difference : flaot
        The results of the fitness function.
        The smaller the value, the higher the fitness.

    Notes
    -----
    A fitness function is a particular type of objective function that is used to summarise,
    as a single figure of merit, how close a given design solution is to achieving the set aims.
    Fitness functions are used in genetic programming and genetic algorithms to guide
    simulations towards optimal design solutions.

    https://en.wikipedia.org/wiki/Fitness_function

    References
    ----------
    "Malware detection based on dependency graph using hybrid genetic algorithm",
    by K.Kim and B.Moon (2010)
    http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

    Programmers
    -----------
    Stu L.Akirav & B.Schtalman

    Example: finding the maximum subgraph isomorphism on two graphs 
    -----------------------------------------------------------------
    >>> import networkx as nx

    # basic_code
    >>> basic_RG = nx.DiGraph()
    >>> basic_RG.add_nodes_from(range(6, 10))
    >>> edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    >>> basic_RG.add_edges_from(edges)

    # basic_code_v1 
    >>> basic_RG_v1 = nx.DiGraph()
    >>> basic_RG_v1.add_nodes_from(range(6, 10))
    >>> edges = [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
    >>> basic_RG_v1.add_edges_from(edges)

    # calculates the number of nodes and edges of the originl graphs 
    >>> basic_num_of_nodes = len(basic_RG.nodes)
    >>> basic_num_of_edges = len(basic_RG.edges)

    # runs the function
    >>> fitness(basic_RG, basic_RG_v1, basic_num_of_nodes, basic_num_of_edges, basic_num_of_nodes, basic_num_of_edges)
    0.0
    """

    logging.info('Started calculating fitness')
    if nx.is_isomorphic(sub_G1, sub_G2):
        logging.debug('Graphs are isomorphic')
        min_val = 0
        if G1_num_of_nodes < G2_num_of_nodes:
            min_val = G1_num_of_edges
        else:
            min_val = G2_num_of_edges
        mutual = len(sub_G2.edges)
        logging.debug(f'Calculating fitness value: {(((G1_num_of_edges - mutual) + (G2_num_of_edges - mutual)) / min_val)}')
        return (((G1_num_of_edges - mutual) + (G2_num_of_edges - mutual)) / min_val)
    else:
        logging.debug('Graphs are not isomorphic')
        return 999999 # arbitrary high number

