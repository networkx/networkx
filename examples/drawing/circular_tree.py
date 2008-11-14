import networkx as nx
import matplotlib.pyplot as plt

try:
    from networkx import graphviz_layout
except ImportError:
    raise ImportError("This example needs Graphviz and either PyGraphviz or Pydot")


G=nx.balanced_tree(3,5)
pos=nx.graphviz_layout(G,prog='twopi',args='')
plt.figure(figsize=(8,8))
nx.draw(G,pos,node_size=20,alpha=0.5,node_color="blue", with_labels=False)
plt.axis('equal')
plt.savefig('circular_tree.png')
plt.show()

