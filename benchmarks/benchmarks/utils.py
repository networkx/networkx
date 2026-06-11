import random

import networkx as nx

# Cache for the drug-interaction network so it is downloaded at most once per
# benchmark process (and never at import/discovery time).
_drug_interaction_network = None


def benchmark_name_from_func_call(func, *args, **kwargs) -> str:
    """Generate a string name for a graph-generating function and its arguments.

    This function takes a graph constructor (such as a NetworkX generator),
    along with its positional and keyword arguments, and returns a string
    of the form: 'function_name(arg1, arg2, ..., kwarg1=val1, ...)'.

    Parameters:
        func (Callable): The graph-generating function.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        str: A string representation of the function and its arguments,
             suitable for labeling graphs in benchmarks or plots.

    Example:
        >>> _benchmark_name_from_func_call(nx.erdos_renyi_graph, 100, 0.1)
        'erdos_renyi_graph(100, 0.1)'

        >>> _benchmark_name_from_func_call(nx.grid_2d_graph, 5, 5, periodic=True)
        'grid_2d_graph(5, 5, periodic=True)'
    """

    def to_str(value):
        if callable(value):
            return value.__name__
        else:
            return str(value)

    args_str = ", ".join(map(to_str, args))
    kwargs_str = ", ".join(f"{k}={to_str(v)}" for k, v in kwargs.items())
    all_args = ", ".join(filter(None, [args_str, kwargs_str]))
    return f"{to_str(func)}({all_args})"


def weighted_graph(weight_seed, graph_func, *args, **kwargs) -> nx.Graph:
    """
    Generate a graph using the given function and assign random edge weights.

    Parameters:
        weight_seed (int): Seed for the random number generator.
        graph_func (Callable): The graph-generating function.
        *args: Positional arguments for the graph function.
        **kwargs: Keyword arguments for the graph function.

    Returns:
        nx.Graph: A graph with randomly weighted edges.
    """
    rng = random.Random(weight_seed)
    G = graph_func(*args, **kwargs)
    for u, v in G.edges():
        G[u][v]["weight"] = rng.randint(1, len(G))
    return G


def fetch_drug_interaction_network():
    """Return the SNAP drug-drug interaction network, downloaded on first use.

    The dataset is fetched lazily (not at import time) and cached, so that asv
    benchmark *discovery* never depends on network access. If the download
    fails (e.g. transient SNAP outage or a sandboxed runner), this raises
    ``NotImplementedError`` so asv skips only the dependent benchmark instead of
    failing the entire suite.

    Dataset: https://snap.stanford.edu/biodata/datasets/10001/10001-ChCh-Miner.html
    """
    global _drug_interaction_network
    if _drug_interaction_network is None:
        # pandas is imported here rather than at module level so the benchmark
        # suite can be imported/discovered without pandas installed.
        import pandas as pd

        url = "https://snap.stanford.edu/biodata/datasets/10001/files/ChCh-Miner_durgbank-chem-chem.tsv.gz"
        try:
            data = pd.read_csv(url, sep="\t", header=None)
        except Exception as exc:  # network/IO/parse failure
            msg = f"could not download drug interaction dataset: {exc}"
            raise NotImplementedError(msg) from exc
        _drug_interaction_network = nx.from_pandas_edgelist(data, source=0, target=1)
    return _drug_interaction_network
