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
    
    def test_lf(self):
        lf = nx.Graph()
        lf.add_nodes_from([1, 2, 3])
        lf.add_edges_from([
            (1, 2),
            (1, 3),
            (2, 3)
        ])
        
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

        