import networkx as nx
from networkx.algorithms.flow import edmonds_karp, network_simplex

#Setting up Graph
G = nx.DiGraph()
G.add_edge("A", "B", my_cap=10, weight=1)
G.add_edge("B", "C", my_cap=5, weight=1)

# Defining a Callable Capacity
def get_capacity(u, v, attr):
    print("Called")
    return attr.get('my_cap', 0)

print("--- Testing Edmonds-Karp (Control) ---")
try:
    R = edmonds_karp(G, "A", "C", capacity=get_capacity)
    print(f"Success! Flow value: {R.graph['flow_value']}")
except Exception as e:
    print(f"Edmonds-Karp Failed: {e}")

print("\n--- Testing Network Simplex (Target) ---")
#adding demands for min-cost flow
G.nodes["A"]['demand'] = -5
G.nodes["C"]['demand'] = 5

try:
    cost, flow = network_simplex(G, capacity=get_capacity)
    print(f"Network Simplex Cost: {cost}")
except Exception as e:
    print(f"Network Simplex Crashed: {e}")