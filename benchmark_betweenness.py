import time
import networkx as nx

def run_benchmark(n=1000, p=0.01, k=10):
    G = nx.gnp_random_graph(n, p, seed=42)

    start = time.perf_counter()
    bc = nx.betweenness_centrality(G, k=k, normalized=True, seed=42)
    end = time.perf_counter()

    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())
    print("k:", k)
    print("Time:", round(end - start, 3), "seconds")
    print("Sample:", list(bc.items())[:5])

if __name__ == "__main__":
    run_benchmark(n=1000, p=0.01, k=10)