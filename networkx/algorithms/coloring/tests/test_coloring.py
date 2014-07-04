# -*- coding: utf-8 -*-
"""Greedy coloring test suite.

Run with nose: nosetests -v test_coloring.py
"""

__author__ = "\n".join(["Christian Olsson <chro@itu.dk>",
                        "Jan Aagaard Meier <jmei@itu.dk>",
                        "Henrik Haugbølle <hhau@itu.dk>"])

import networkx as nx
from nose.tools import *

class TestColoring:
############################## RS tests ##############################
    def test_rs_empty(self):
        graph = emptyGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_random_sequential, interchange=False)
        assert_true(verify_length(coloring, 0))
        assert_true(verify_coloring(graph, coloring))

    def test_rs_oneNode(self):
        graph = oneNodeGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_random_sequential, interchange=False)
        assert_true(verify_length(coloring, 1))
        assert_true(verify_coloring(graph, coloring))

    def test_rs_twoNodes(self):
        graph = twoNodesGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_random_sequential, interchange=False)
        assert_true(verify_length(coloring, 2))
        assert_true(verify_coloring(graph, coloring))

    def test_rs_threeNodeClique(self):
        graph = threeNodeClique()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_random_sequential, interchange=False)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

    def test_rs_shc(self):
        graph = rs_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_random_sequential, interchange=False)
        assert_true(verify_length(coloring, 2) or verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

############################## SLF tests ##############################
    def test_slf_empty(self):
        graph = emptyGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_saturation_largest_first, interchange=False)
        assert_true(verify_length(coloring, 0))
        assert_true(verify_coloring(graph, coloring))

    def test_slf_oneNode(self):
        graph = oneNodeGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_saturation_largest_first, interchange=False)
        assert_true(verify_length(coloring, 1))
        assert_true(verify_coloring(graph, coloring))

    def test_slf_twoNodes(self):
        graph = twoNodesGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_saturation_largest_first, interchange=False)
        assert_true(verify_length(coloring, 2))
        assert_true(verify_coloring(graph, coloring))

    def test_slf_threeNodeClique(self):
        graph = threeNodeClique()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_saturation_largest_first, interchange=False)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

    def test_slf_shc(self):
        graph = slf_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_saturation_largest_first, interchange=False)
        assert_true(verify_length(coloring, 3) or verify_length(coloring, 4))
        assert_true(verify_coloring(graph, coloring))

    def test_slf_hc(self):
        graph = slf_hc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_saturation_largest_first, interchange=False)
        assert_true(verify_length(coloring, 4))
        assert_true(verify_coloring(graph, coloring))

############################## LF tests ##############################
    def test_lf_empty(self):
        graph = emptyGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_largest_first, interchange=False)
        assert_true(verify_length(coloring, 0))
        assert_true(verify_coloring(graph, coloring))

    def test_lf_oneNode(self):
        graph = oneNodeGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_largest_first, interchange=False)
        assert_true(verify_length(coloring, 1))
        assert_true(verify_coloring(graph, coloring))

    def test_lf_twoNodes(self):
        graph = twoNodesGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_largest_first, interchange=False)
        assert_true(verify_length(coloring, 2))
        assert_true(verify_coloring(graph, coloring))

    def test_lf_threeNodeClique(self):
        graph = threeNodeClique()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_largest_first, interchange=False)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

    def test_lf_shc(self):
        graph = lf_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_largest_first, interchange=False)
        assert_true(verify_length(coloring, 2) or verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))
        
    def test_lf_hc(self):
        graph = lf_hc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_largest_first, interchange=False)
        assert_true(verify_length(coloring, 4))
        assert_true(verify_coloring(graph, coloring))

############################## SL tests ##############################
    def test_sl_empty(self):
        graph = emptyGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_smallest_last, interchange=False)
        assert_true(verify_length(coloring, 0))
        assert_true(verify_coloring(graph, coloring))

    def test_sl_oneNode(self):
        graph = oneNodeGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_smallest_last, interchange=False)
        assert_true(verify_length(coloring, 1))
        assert_true(verify_coloring(graph, coloring))

    def test_sl_twoNodes(self):
        graph = twoNodesGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_smallest_last, interchange=False)
        assert_true(verify_length(coloring, 2))
        assert_true(verify_coloring(graph, coloring))

    def test_sl_threeNodeClique(self):
        graph = threeNodeClique()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_smallest_last, interchange=False)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

    def test_sl_shc(self):
        graph = sl_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_smallest_last, interchange=False)
        assert_true(verify_length(coloring, 3) or verify_length(coloring, 4))
        assert_true(verify_coloring(graph, coloring))
    
    def test_sl_hc(self):
        graph = sl_hc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_smallest_last, interchange=False)
        assert_true(verify_length(coloring, 5))
        assert_true(verify_coloring(graph, coloring))
        
############################## GIS tests ##############################
    def test_gis_empty(self):
        graph = emptyGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_independent_set, interchange=False)
        assert_true(verify_length(coloring, 0))
        assert_true(verify_coloring(graph, coloring))

    def test_gis_oneNode(self):
        graph = oneNodeGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_independent_set, interchange=False)
        assert_true(verify_length(coloring, 1))
        assert_true(verify_coloring(graph, coloring))

    def test_gis_twoNodes(self):
        graph = twoNodesGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_independent_set, interchange=False)
        assert_true(verify_length(coloring, 2))
        assert_true(verify_coloring(graph, coloring))

    def test_gis_threeNodeClique(self):
        graph = threeNodeClique()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_independent_set, interchange=False)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

    def test_gis_shc(self):
        graph = gis_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_independent_set, interchange=False)
        assert_true(verify_length(coloring, 2) or verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

    def test_gis_hc(self):
        graph = gis_hc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_independent_set, interchange=False)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

############################## CS tests ##############################
    def test_cs_empty(self):
        graph = emptyGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential, interchange=False)
        assert_true(verify_length(coloring, 0))
        assert_true(verify_coloring(graph, coloring))

    def test_cs_oneNode(self):
        graph = oneNodeGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential, interchange=False)
        assert_true(verify_length(coloring, 1))
        assert_true(verify_coloring(graph, coloring))

    def test_cs_twoNodes(self):
        graph = twoNodesGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential, interchange=False)
        assert_true(verify_length(coloring, 2))
        assert_true(verify_coloring(graph, coloring))

    def test_cs_threeNodeClique(self):
        graph = threeNodeClique()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential, interchange=False)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

    def test_cs_shc(self):
        graph = cs_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential, interchange=False)
        assert_true(verify_length(coloring, 3) or verify_length(coloring, 4))
        assert_true(verify_coloring(graph, coloring))

    def test_cs_dfs_empty(self):
        graph = emptyGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential_dfs, interchange=False)
        assert_true(verify_length(coloring, 0))
        assert_true(verify_coloring(graph, coloring))

    def test_cs_dfs_oneNode(self):
        graph = oneNodeGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential_dfs, interchange=False)
        assert_true(verify_length(coloring, 1))
        assert_true(verify_coloring(graph, coloring))

    def test_cs_dfs_twoNodes(self):
        graph = twoNodesGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential_dfs, interchange=False)
        assert_true(verify_length(coloring, 2))
        assert_true(verify_coloring(graph, coloring))

    def test_cs_dfs_threeNodeClique(self):
        graph = threeNodeClique()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential_dfs, interchange=False)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

    def test_cs_dfs_shc(self):
        graph = cs_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential_dfs, interchange=False)
        assert_true(verify_length(coloring, 3) or verify_length(coloring, 4))
        assert_true(verify_coloring(graph, coloring))

    def test_cs_disconnected(self):
        # _connected_ sequential should still work on disconnected graphs
        graph = nx.Graph()
        graph.add_edges_from([
            (1, 2),
            (2, 3),
            (4, 5),
            (5, 6)
        ])
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential, interchange=False)
        assert_true(verify_length(coloring, 2))
        assert_true(verify_coloring(graph, coloring))


############################## Interchange tests ##############################
# RSI
    def test_rsi_empty(self):
        graph = emptyGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_random_sequential, interchange=True)
        assert_true(verify_length(coloring, 0))
        assert_true(verify_coloring(graph, coloring))

    def test_rsi_oneNode(self):
        graph = oneNodeGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_random_sequential, interchange=True)
        assert_true(verify_length(coloring, 1))
        assert_true(verify_coloring(graph, coloring))

    def test_rsi_twoNodes(self):
        graph = twoNodesGraph()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_random_sequential, interchange=True)
        assert_true(verify_length(coloring, 2))
        assert_true(verify_coloring(graph, coloring))

    def test_rsi_threeNodeClique(self):
        graph = threeNodeClique()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_random_sequential, interchange=True)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

    def test_rsi_rsshc(self):
        graph = rs_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_random_sequential, interchange=True)
        assert_true(verify_length(coloring, 2))
        assert_true(verify_coloring(graph, coloring))

    def test_rsi_shc(self):
        graph = rsi_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_random_sequential, interchange=True)
        assert_true(verify_length(coloring, 3) or verify_length(coloring, 4))
        assert_true(verify_coloring(graph, coloring))
# SLFI
    def test_slfi_slfshc(self):
        graph = oneNodeGraph()
        assert_raises(nx.NetworkXPointlessConcept, nx.coloring.greedy_color, graph, strategy=nx.coloring.strategy_saturation_largest_first, interchange=True)

# LFI
    def test_lfi_lfshc(self):
        graph = lf_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_largest_first, interchange=True)
        assert_true(verify_length(coloring, 2))
        assert_true(verify_coloring(graph, coloring))        
    
    def test_lfi_lfhc(self):
        graph = lf_hc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_largest_first, interchange=True)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))
        
    def test_lfi_shc(self):
        graph = lfi_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_largest_first, interchange=True)
        assert_true(verify_length(coloring, 3) or verify_length(coloring, 4))
        assert_true(verify_coloring(graph, coloring))

    def test_lfi_hc(self):
        graph = lfi_hc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_largest_first, interchange=True)
        assert_true(verify_length(coloring, 4))
        assert_true(verify_coloring(graph, coloring))
# SLI
    def test_sli_slshc(self):
        graph = sl_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_smallest_last, interchange=True)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))
    
    def test_sli_slhc(self):
        graph = sl_hc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_smallest_last, interchange=True)
        assert_true(verify_length(coloring, 4))
        assert_true(verify_coloring(graph, coloring))
        
    def test_sli_shc(self):
        graph = sli_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_smallest_last, interchange=True)
        assert_true(verify_length(coloring, 3) or verify_length(coloring, 4))
        assert_true(verify_coloring(graph, coloring))

    def test_sli_hc(self):
        graph = sli_hc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_smallest_last, interchange=True)
        assert_true(verify_length(coloring, 5))
        assert_true(verify_coloring(graph, coloring))
#GISI
    def test_gisi_oneNode(self):
        graph = oneNodeGraph()
        assert_raises(nx.NetworkXPointlessConcept, nx.coloring.greedy_color, graph, strategy=nx.coloring.strategy_independent_set, interchange=True)
# CS
    def test_csi_csshc(self):
        graph = cs_shc()
        coloring = nx.coloring.greedy_color(graph, strategy=nx.coloring.strategy_connected_sequential, interchange=True)
        assert_true(verify_length(coloring, 3))
        assert_true(verify_coloring(graph, coloring))

############################## Utility functions ##############################
def verify_coloring(graph, coloring):
    for node in graph.nodes_iter():
        if node not in coloring:
            return False

        color = coloring[node]
        for neighbor in graph.neighbors(node):
            if coloring[neighbor] == color:
                return False

    return True

def verify_length(coloring, expected):
    coloring = dict_to_sets(coloring)
    return len(coloring) == expected

def dict_to_sets(colors):
    if len(colors) == 0:
        return []

    k = max(colors.values()) + 1
    sets = [set() for _ in range(k)]

    for (node, color) in colors.items():
        sets[color].add(node)

    return sets

############################## Graphs ##############################
def emptyGraph():
    return nx.Graph()

def oneNodeGraph():
    graph = nx.Graph()
    graph.add_nodes_from([1])
    return graph

def twoNodesGraph():
    graph = nx.Graph()
    graph.add_nodes_from([1,2])
    graph.add_edges_from([(1,2)])
    return graph

def threeNodeClique():
    graph = nx.Graph()
    graph.add_nodes_from([1,2, 3])
    graph.add_edges_from([(1,2), (1,3), (2,3)])
    return graph

def rs_shc():
    graph = nx.Graph()
    graph.add_nodes_from([1,2,3,4])
    graph.add_edges_from([
        (1,2),
        (2,3),
        (3,4)
    ])
    return graph

def slf_shc():
    graph = nx.Graph()
    graph.add_nodes_from([1,2,3,4,5,6,7])
    graph.add_edges_from([
        (1,2),
        (1,5),
        (1,6),
        (2,3),
        (2,7),
        (3,4),
        (3,7),
        (4,5),
        (4,6),
        (5,6)
    ])
    return graph

def slf_hc():
    graph = nx.Graph()
    graph.add_nodes_from([1,2,3,4,5,6,7,8])
    graph.add_edges_from([
        (1,2),
        (1,3),
        (1,4),
        (1,5),
        (2,3),
        (2,4),
        (2,6),
        (5,7),
        (5,8),
        (6,7),
        (6,8),
        (7,8)  
    ])
    return graph    

def lf_shc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6])
    graph.add_edges_from([
        (6, 1),
        (1, 4),
        (4, 3),
        (3, 2),
        (2, 5)
    ])
    return graph

def lf_hc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
    graph.add_edges_from([
        (1, 7),
        (1, 6),
        (1, 3),
        (1, 4),
        (7, 2),
        (2, 6),
        (2, 3),
        (2, 5),
        (5, 3),
        (5, 4),
        (4, 3)
    ])
    return graph
    
def sl_shc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6])
    graph.add_edges_from([
        (1, 2),
        (1, 3),
        (2, 3),
        (1, 4),
        (2, 5),
        (3, 6),
        (4, 5),
        (4, 6),
        (5, 6)
    ])
    return graph

def sl_hc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
    graph.add_edges_from([
        (1, 2),
        (1, 3),
        (1, 5),
        (1, 7),
        (2, 3),
        (2, 4),
        (2, 8),
        (8, 4),
        (8, 6),
        (8, 7),
        (7, 5),
        (7, 6),
        (3, 4),
        (4, 6),
        (6, 5),
        (5, 3)
    ])
    return graph

def gis_shc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4])
    graph.add_edges_from([
        (1, 2),
        (2, 3),
        (3, 4)
    ])
    return graph

def gis_hc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6])
    graph.add_edges_from([
        (1, 5),
        (2, 5),
        (3, 6),
        (4, 6),
        (5, 6)
    ])
    return graph

def cs_shc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5])
    graph.add_edges_from([
        (1, 2),
        (1, 5),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 4),
        (4, 5)
    ])
    return graph

def rsi_shc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6])
    graph.add_edges_from([
        (1, 2),
        (1, 5),
        (1, 6),
        (2, 3),
        (3, 4),
        (4, 5),
        (4, 6),
        (5, 6)
    ])
    return graph

def lfi_shc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
    graph.add_edges_from([
        (1, 2),
        (1, 5),
        (1, 6),
        (2, 3),
        (2, 7),
        (3, 4),
        (3, 7),
        (4, 5),
        (4, 6),
        (5, 6)
    ])
    return graph

def lfi_hc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9])
    graph.add_edges_from([
        (1, 2),
        (1, 5),
        (1, 6),
        (1, 7),
        (2, 3),
        (2, 8),
        (2, 9),
        (3, 4),
        (3, 8),
        (3, 9),
        (4, 5),
        (4, 6),
        (4, 7),
        (5, 6)
    ])
    return graph

def sli_shc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
    graph.add_edges_from([
        (1, 2),
        (1, 3),
        (1, 5),
        (1, 7),
        (2, 3),
        (2, 6),
        (3, 4),
        (4, 5),
        (4, 6),
        (5, 7),
        (6, 7)
    ])
    return graph

def sli_hc():
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9])
    graph.add_edges_from([
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (2, 3),
        (2, 7),
        (2, 8),
        (2, 9),
        (3, 6),
        (3, 7),
        (3, 9),
        (4, 5),
        (4, 6),
        (4, 8),
        (4, 9),
        (5, 6),
        (5, 7),
        (5, 8),
        (6, 7),
        (6, 9),
        (7, 8),
        (8, 9)
    ])
    return graph

