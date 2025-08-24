import random

import pandas as pd

import networkx as nx


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
    # Drug-drug interaction network
    # https://snap.stanford.edu/biodata/datasets/10001/10001-ChCh-Miner.html
    data = pd.read_csv(
        "https://snap.stanford.edu/biodata/datasets/10001/files/ChCh-Miner_durgbank-chem-chem.tsv.gz",
        sep="\t",
        header=None,
    )
    return nx.from_pandas_edgelist(data, source=0, target=1)
