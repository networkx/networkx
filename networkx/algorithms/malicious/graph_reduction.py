"""
Building a reduced graph from a dependency graph.
"""

__all__ = ["build_RG_from_DG"]

import logging

LOGֹ_FORMAT = "%(levelname)s, time: %(asctime)s , line: %(lineno)d- %(message)s "
# create and configure logger
logging.basicConfig(filename='malicious_algo_logging.log', level=logging.DEBUG, filemode='w')
logger = logging.getLogger()
def build_RG_from_DG(G):
  """
  Building a reduced graph (RG) from a dependency graph (DG).
  The function returns the RG.

  Parameters
  ----------
  G : NetworkX DiGraph
      A (dirceted) dependency graph 

  Returns
  -------
  g_tag : NetworkX DiGraph
      A (dirceted) reduced graph    

  Notes
  -----
  The size of a dependency graph may be reduced. Some
  part of the code where the control flow never reaches can
  be removed. In addition, vertices that satisfy one of the
  following four conditions can be eliminated:
      • A vertex with only one outgoing edge without any incoming
        edge. It is mostly the declaration of a variable,
        which is not critical when only considering the core
        part of the program.
      • A vertex with only one incoming edge without any
        outgoing edge. It means that the first vertex uses the
        value of the latter one.
      • A vertex with only one incoming and one outgoing
        edge. It plays a role in conveying a value or data from
        one vertex to another mainly.

  http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

  References
  ----------
  "Malware detection based on dependency graph using hybrid genetic algorithm",
  by K.Kim and B.Moon (2010)
  http://rosaec.snu.ac.kr/publish/2010/T2/KiMo-GECCO-2010.pdf

  Programmers
  -----------
  Stu L.Akirav & B.Schtalman

  Example 1: building a RG graph
  ------------------------------
  >>> import networkx as nx

  # creates and builds the DG graph
  >>> directed_G1 = nx.DiGraph()
  >>> directed_G1.add_nodes_from(range(1,12))
  >>> directed_G1.add_edges_from([(1, 4),(2, 5),(3, 6),(4, 7),(5, 8),(6, 7),(6, 8),(6, 9),(8, 8),(9, 7),(9, 8),(9,9)])

  # creates and builds the RG graph by removing irrelevant edges and nodes from the DG graph 
  >>> reduction_G1 = directed_G1
  >>> reduction_G1.remove_edges_from([(1,4),(2,5),(3,6),(4, 7),(5, 8)])
  >>> reduction_G1.remove_nodes_from([1,2,3,4,5,10,11])

  >>> print(build_RG_from_DG(directed_G1).edges)
  [(6, 7), (6, 8), (6, 9), (8, 8), (9, 7), (9, 8), (9, 9)]
  
  Example 2: a graph that can not be reduced (the original graph will be returned)
  ------------------------------------------------------------------------------
  # creates and builds the DG graph
  >>> directed_G2 = nx.DiGraph()
  >>> directed_G2.add_nodes_from(range(1,7))
  >>> directed_G2.add_edges_from([(1,2),(2,3)])
  >>> print(build_RG_from_DG(directed_G2).edges)
  [(1, 2), (2, 3)]
  """
  
  logging.info('Started building reduced graph from directed graph')

  nodes_to_remove = []  # contains all the nodes that should be removed
  isolated_nodes = []  # contains all the nodes that does not has any edge
  for v in G.nodes:
    logging.debug(
        f'checking node: {v}')
    edges_in = G.in_degree(v)
    edges_out = G.out_degree(v)
    if edges_in <= 1 and edges_out <= 1:  # checks for each node if it should be removed
      if edges_in == 0 and edges_out == 0:
        isolated_nodes.append(v)
        logging.debug("append to isolated_nodes")
      else:
        nodes_to_remove.append(v)
        logging.debug("append to nodes_to_remove")
        
  # removes all the islolated nodes from G
  G.remove_nodes_from(isolated_nodes)
  logging.debug(
      f'Removed {len(isolated_nodes)} isolated nodes from the graph')
  # in case that all the nodes should be removed, we will return the original graph without the isolated nodes
  if len(nodes_to_remove) == len(G.nodes):
      logging.debug(f'All nodes were marked for removal. Returning original graph without isolated nodes: {G.nodes}')
      return G
  # otherwise, we will remove those nodes as well
  else:
      g_tag = G
      g_tag.remove_nodes_from(nodes_to_remove)
      logging.debug(
          f'Removed {len(nodes_to_remove)} nodes from the graph. Returning g_tag: {g_tag.nodes}')
      return g_tag


# Set the logging level to INFO
logging.basicConfig(level=logging.INFO)
