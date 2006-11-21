"""
NetworkX
========

   NetworkX (NX) is a Python package for the creation, manipulation, and
   study of the structure, dynamics, and functions of complex networks.  


Using 
-----

   Just write in Python

   >>> import networkx as NX
   >>> G=NX.Graph()
   >>> G.add_edge(1,2)
   >>> G.add_node("spam")
   >>> print G.nodes()
   [1, 2, 'spam']
   >>> print G.edges()
   [(1, 2)]

See networkx.base for the details of the API.


"""
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#
# Add platform dependent shared library path to sys.path
#
import sys
#import os, sys
#sys.path.append(os.path.join(os.path.split(__file__)[0], sys.platform))
if sys.version_info[:2] < (2, 3):
    print "Python version 2.3 or later is required for NetworkX (%d.%d detected)." %  sys.version_info[:2]
    sys.exit(-1)
#del os
del sys
# Release data
import release  # do it explicitly so pydoc can see it - pydoc bug
__version__  = release.version
__date__     = release.date
__author__   = '%s <%s>\n%s <%s>\n%s <%s>' % \
              ( release.authors['Hagberg'] + release.authors['Schult'] + \
                release.authors['Swart'] )
__license__  = release.license



#
# NetworkX package modules
#
from exception import  NetworkXException, NetworkXError
from graph import Graph
from digraph import DiGraph
from function import  nodes, edges, degree, degree_histogram, neighbors,\
                 number_of_nodes, number_of_edges, density,\
                 nodes_iter, edges_iter, is_directed
from xgraph import XGraph
from xdigraph import XDiGraph
from distance import eccentricity, diameter, radius, periphery, center
from shortest_path import  \
     shortest_path, shortest_path_length,bidirectional_shortest_path,\
     single_source_shortest_path, single_source_shortest_path_length,\
     all_pairs_shortest_path, all_pairs_shortest_path_length,\
     dijkstra_path, dijkstra_path_length, bidirectional_dijkstra,\
     single_source_dijkstra_path, single_source_dijkstra_path_length,\
     single_source_dijkstra,\
     predecessor, floyd_warshall,\
     bfs, dfs
from dag import \
     topological_sort, topological_sort_recursive,\
     is_directed_acyclic_graph
from component import \
     number_connected_components, connected_components,\
     is_connected, connected_component_subgraphs,\
     node_connected_component
from search import dfs_preorder, dfs_postorder, dfs_predecessor,\
            dfs_successor, bfs_length, bfs_path, dfs_forest
from cluster import triangles, average_clustering, clustering, transitivity
from operators import union, cartesian_product, compose, complement,\
                      disjoint_union, create_empty_copy,\
                      subgraph, convert_to_undirected, convert_to_directed,\
                      convert_node_labels_to_integers, relabel_nodes
from centrality import betweenness_centrality, \
                       degree_centrality, \
                       closeness_centrality
from hybrid import kl_connected_subgraph, is_kl_connected

# need numpy for spectrum
try:
    from spectrum import \
         adj_matrix, laplacian, generalized_laplacian,\
         laplacian_spectrum, adjacency_spectrum
except ImportError:
    pass

from utils import is_string_like, iterable,\
                  pareto_sequence, powerlaw_sequence, uniform_sequence,\
                  cumulative_distribution, discrete_sequence
from io import write_gpickle, read_gpickle, \
   read_edgelist, write_edgelist, \
   read_multiline_adjlist, write_multiline_adjlist, \
   read_adjlist, write_adjlist,\
   read_yaml, write_yaml

from convert import from_whatever,\
     from_dict_of_dicts, to_dict_of_dicts,\
     from_dict_of_lists, to_dict_of_lists,\
     from_numpy_matrix, to_numpy_matrix,\
     from_scipy_sparse_matrix, to_scipy_sparse_matrix

# import some useful graphs - we always use these...
from generators.classic import *
from generators.small import *
from generators.random_graphs import *
from generators.degree_seq import *
from generators.directed import *
from drawing import *

from tests import run as test
