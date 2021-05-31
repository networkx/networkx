"""
==========================
Traveling Salesman Problem
==========================

This is an example of a drawing solution of the traveling salesman problem

The function is used to produce the solution is greedy_tsp,
where given a set of nodes and a source, it calculates the route of the nodes
that the traveler has to follow in order to minimize the total cost.
The criteria is that in every iteration choose the next node to be the closest one
to the latest on the current route (Nearest Neighbor).
"""

import matplotlib.pyplot as plt
import networkx as nx
import networkx.algorithms.approximation as nx_app
import random
import math

G = nx.DiGraph()

total_nodes = 10
pos = {}
random.seed(1)
for n in range(0, total_nodes):
    x = random.randint(0, 100)
    y = random.randint(0, 100)
    pos.update({n: (x, y)})
G.add_nodes_from(pos.keys())

for i in range(0, total_nodes):
    for j in range(0, total_nodes):
        if i == j:
            continue
        dist = math.sqrt(
            math.pow(pos[i][0] - pos[j][0], 2) + math.pow(pos[i][1] - pos[j][1], 2)
        )
        dist = round(dist)
        G.add_edge(i, j, weight=dist)
nodes_labels = {x: x for x in pos.keys()}
nx.draw_networkx_nodes(G, pos, node_size=200)
nx.draw_networkx_labels(G, pos, labels=nodes_labels)

cycle = nx_app.greedy_tsp(G, source=0)

edge_list = [(x1, x2) for x1, x2 in nx.utils.pairwise(cycle)]

nx.draw_networkx_edges(G, pos, edge_color="blue", width=0.5, arrows=False)
nx.draw_networkx(
    G,
    pos,
    arrows=True,
    with_labels=True,
    nodelist=set(cycle),
    edgelist=edge_list,
    edge_color="red",
    node_size=200,
    width=4,
)
plt.show()
