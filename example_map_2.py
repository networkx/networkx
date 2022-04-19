#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

G = nx.Graph()

G.add_nodes_from([
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '9',
    '10',
    ])

G.add_edges_from([
    ('1', '2'),
    ('7', '2'),
    ('3', '9'),
    ('3', '2'),
    ('7', '6'),
    ('5', '2'),
    ('1', '5'),
    ('2', '8'),
    ('10', '2'),
    ('1', '7'),
    ('6', '1'),
    ('6', '9'),
    ('8', '4'),
    ('9', '4'),
    ])

from networkx.algorithms import approximation as apxa

I = apxa.maximum_independent_set(G)
M = apxa.min_maximal_matching(G)

color_map_1 = []
for node in G:
    if node in I:
        color_map_1.append('red')
    else:
        color_map_1.append('grey')

color_map_2 = []
for edge in G.edges:
    if edge in M:
        color_map_2.append('red')
    else:
        color_map_2.append('grey')

(fig, axs) = plt.subplots(ncols=2, figsize=(3, 2),
                          gridspec_kw={'width_ratios': [1, 1]})

nx.draw(
    G,
    with_labels=True,
    node_size=50,
    font_size=25,
    edge_color='grey',
    node_color=color_map_1,
    ax=axs[0],
    )

nx.draw(
    G,
    with_labels=True,
    node_size=50,
    font_size=25,
    edge_color=color_map_2,
    node_color='grey',
    ax=axs[1],
    )

axs[0].set_title('Clique - Maximum Independent Set\nMaximum set of (red) vertices with no edge     connecting them'
                 )
axs[1].set_title('Matching\nMaximal set of pairwise non-adjacent (red) edges'
                 )
plt.show()
