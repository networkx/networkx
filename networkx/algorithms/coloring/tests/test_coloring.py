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
    
    def test_lf_shc(self):
        lf_shc = nx.Graph()
        lf_shc.add_nodes_from([1, 2, 3, 4, 5, 6])
        lf_shc.add_edges_from([
            (6, 1),
            (1, 4),
            (4, 3),
            (3, 2),
            (2, 5)
        ])
        
        coloring = nx.coloring(lf_shc, strategy='lf', interchange=False, returntype='sets')
        assert_true(len(coloring) <= 3)
        
    def test_lf_hc(self):
        lf_hc = nx.Graph()
        lf_hc.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
        lf_hc.add_edges_from([
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
        
        coloring = nx.coloring(lf_hc, strategy='lf', interchange=False, returntype='sets')
        # this is wrong
        assert_true(len(coloring) == 4)
        
    
    def test_sl_shc(self):
        sl_shc = nx.Graph()
        sl_shc.add_nodes_from([1, 2, 3, 4, 5, 6])
        sl_shc.add_edges_from([
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
        
        coloring = nx.coloring(sl_shc, strategy='sl', interchange=False, returntype='sets')
        assert_true(len(coloring) <= 4)
    
    def test_sl_hc(self):
        sl_hc = nx.Graph()
        sl_hc.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
        sl_hc.add_edges_from([
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
        
        coloring = nx.coloring(sl_hc, strategy='sl', interchange=False, returntype='sets')
        assert_true(len(coloring) == 5)
        
    def test_gis_shtc(self):
        gis_shtc = nx.Graph()
        gis_shtc.add_nodes_from([1, 2, 3, 4])
        gis_shtc.add_edges_from([
            (1, 2),
            (2, 3),
            (3, 4)
        ])

        coloring = nx.coloring(gis_shtc, strategy='gis', interchange=False, returntype='sets')
        assert_true(len(coloring) <= 3)

    def test_gis_htc(self):
        gis_htc = nx.Graph()
        gis_htc.add_nodes_from([1, 2, 3, 4, 5, 6])
        gis_htc.add_edges_from([
            (1, 5),
            (2, 5),
            (3, 6),
            (4, 6),
            (5, 6)
        ])

        coloring = nx.coloring(gis_htc, strategy='gis', interchange=False, returntype='sets')
        assert_equal(len(coloring), 3)

    def test_cs_shtc(self):
        cs_shtc = nx.Graph()
        cs_shtc.add_nodes_from([1, 2, 3, 4, 5])
        cs_shtc.add_edges_from([
            (1, 2),
            (1, 5),
            (2, 3),
            (2, 4),
            (3, 4),
            (4, 5)
        ])

        coloring = nx.coloring(cs_shtc, strategy='cs', interchange=False, returntype='sets')
        assert_true(len(coloring) <= 3)


    def test_cs_htc(self):
        pass

        