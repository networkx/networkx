"""
==================
SNAP Graph Summary
==================
Examples of summarizing a graph based on node attributes and edge attributes.
Nodes in graphs are grouped such that nodes with the same attributes are in the
same group.  Then the groups are split until all nodes in all groups have
relationships with the same groups, producing a lossless summarization.
"""
import networkx as nx
from networkx.algorithms import summarization
import matplotlib.pyplot as plt

plt.suptitle("SNAP Summarization")

original_graph = nx.karate_club_graph()

base_options = dict(with_labels=True, edgecolors="black")

ax1 = plt.subplot(1, 2, 1)
plt.title(
    "Original (%s nodes, %s edges)"
    % (original_graph.number_of_nodes(), original_graph.number_of_edges())
)
pos = nx.spring_layout(original_graph)
nx.draw_networkx(original_graph, pos=pos, **base_options)

node_attributes = ("club",)
snap_summarizer = summarization.SNAP.from_graph(original_graph, node_attributes)
summary_graph, supernodes = snap_summarizer.summarize(original_graph, prefix="S-")

plt.subplot(1, 2, 2)

plt.title(
    "SNAP (%s nodes, %s edges)"
    % (summary_graph.number_of_nodes(), summary_graph.number_of_edges())
)
summary_pos = nx.spring_layout(summary_graph)
nx.draw_networkx(summary_graph, pos=summary_pos, **base_options)

plt.tight_layout()
plt.show()
