from networkx.readwrite import json_graph

G = nx.DiGraph([(1, 2)])
data = json_graph.tree_data(G, root=1)

import json

s = json.dumps(data)
