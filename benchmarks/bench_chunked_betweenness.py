import json
import time
import tracemalloc

import networkx as nx


def benchmark_betweenness(graph_type, n, chunk_size=None, **kwargs):
    if graph_type == "erdos_renyi":
        G = nx.erdos_renyi_graph(n, kwargs.get("p", 0.01), seed=42)
    elif graph_type == "barabasi_albert":
        G = nx.barabasi_albert_graph(n, kwargs.get("m", 3), seed=42)
    elif graph_type == "watts_strogatz":
        G = nx.watts_strogatz_graph(
            n, kwargs.get("k", 6), kwargs.get("p", 0.1), seed=42
        )
    else:
        raise ValueError(f"Unknown graph type: {graph_type}")

    tracemalloc.start()
    start_time = time.perf_counter()

    result = nx.betweenness_centrality(G, normalized=False, chunk_size=chunk_size)

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "graph_type": graph_type,
        "n": n,
        "m": G.number_of_edges(),
        "chunk_size": chunk_size,
        "time_sec": end_time - start_time,
        "peak_memory_mb": peak / 1024 / 1024,
        "num_nodes_computed": len(result),
    }


def main():
    results = []

    scenarios = [
        {"graph_type": "erdos_renyi", "n": 100, "p": 0.05},
        {"graph_type": "erdos_renyi", "n": 500, "p": 0.01},
        {"graph_type": "erdos_renyi", "n": 1000, "p": 0.005},
        {"graph_type": "barabasi_albert", "n": 100, "m": 3},
        {"graph_type": "barabasi_albert", "n": 500, "m": 3},
        {"graph_type": "barabasi_albert", "n": 1000, "m": 3},
        {"graph_type": "watts_strogatz", "n": 500, "k": 6, "p": 0.1},
    ]

    chunk_sizes = [None, 10, 50, 100]

    print("Running benchmarks...")
    print("=" * 80)

    for scenario in scenarios:
        graph_type = scenario["graph_type"]
        n = scenario["n"]
        print(f"\nGraph: {graph_type}, n={n}")
        print("-" * 80)

        for chunk_size in chunk_sizes:
            if chunk_size is not None and chunk_size >= n:
                continue

            try:
                result = benchmark_betweenness(**scenario, chunk_size=chunk_size)
                results.append(result)

                chunk_label = f"chunk={chunk_size}" if chunk_size else "standard"
                print(
                    f"  {chunk_label:15s} | "
                    f"Time: {result['time_sec']:6.3f}s | "
                    f"Peak Memory: {result['peak_memory_mb']:6.2f} MB"
                )
            except Exception as e:
                print(f"  Error with chunk_size={chunk_size}: {e}")

    print("\n" + "=" * 80)
    print("SUMMARY - Memory Reduction Analysis")
    print("=" * 80)

    for scenario in scenarios:
        graph_type = scenario["graph_type"]
        n = scenario["n"]

        baseline = next(
            (
                r
                for r in results
                if r["graph_type"] == graph_type
                and r["n"] == n
                and r["chunk_size"] is None
            ),
            None,
        )

        if not baseline:
            continue

        print(f"\n{graph_type} (n={n}):")
        print(
            f"  Baseline: {baseline['peak_memory_mb']:.2f} MB, {baseline['time_sec']:.3f}s"
        )

        for chunk_size in [10, 50, 100]:
            chunked = next(
                (
                    r
                    for r in results
                    if r["graph_type"] == graph_type
                    and r["n"] == n
                    and r["chunk_size"] == chunk_size
                ),
                None,
            )

            if chunked:
                mem_reduction = (
                    1 - chunked["peak_memory_mb"] / baseline["peak_memory_mb"]
                ) * 100
                time_overhead = (chunked["time_sec"] / baseline["time_sec"] - 1) * 100
                print(
                    f"  chunk_size={chunk_size:3d}: "
                    f"Memory: {chunked['peak_memory_mb']:6.2f} MB ({mem_reduction:+5.1f}%), "
                    f"Time: {chunked['time_sec']:6.3f}s ({time_overhead:+5.1f}%)"
                )

    output_file = (
        "D:\\Projects2.0\\Gsoc\\NumFocus\\networkx\\agent_logs\\bench_results.json"
    )
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
