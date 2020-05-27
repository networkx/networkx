import networkx as nx

__all__ = ["distinctiveness"]


def g_preprocess(G, alpha=1):

    try:
        import numpy as np
    except ImportError:
        raise ImportError("distinctiveness requires NumPy ",
                          "http://scipy.org/")

    if isinstance(alpha, list) and len(alpha) == 5:
        alphalist = alpha
    elif isinstance(alpha, (int, float)):
        alphalist = [alpha] * 5
    else:
        raise nx.NetworkXError(
            "Error in the choice of alpha. "
            "Please specify a single number or a list of 5 values."
        )
        return (
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
        )

    # Make an independent copy of the graph
    G = G.copy()

    if G.number_of_nodes() < 3:
        raise nx.NetworkXError("Graph must have at least 3 nodes.")
        return (
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
        )

    # From multigraph to graph
    if type(G) == nx.MultiGraph:
        print("MultiGraph converted to Graph")
        G1 = nx.Graph()
        for u, v, data in G.edges(data=True):
            w = data["weight"] if "weight" in data else 1.0
            if G1.has_edge(u, v):
                G1[u][v]["weight"] += w
            else:
                G1.add_edge(u, v, weight=w)
        G = G1.copy()
    elif type(G) == nx.MultiDiGraph:
        print("MultiDiGraph converted to DiGraph")
        G1 = nx.DiGraph()
        for u, v, data in G.edges(data=True):
            w = data["weight"] if "weight" in data else 1.0
            if G1.has_edge(u, v):
                G1[u][v]["weight"] += w
            else:
                G1.add_edge(u, v, weight=w)
        G = G1.copy()

    # Remove Loops
    loops = nx.selfloop_edges(G)
    if list(loops):
        print("WARNING: Loops will be ignored.")
        G.remove_edges_from(loops)

    # Check if all existing arcs have weights, otherwise assign value of 1
    # Check for negative weights, zero weights and weight lower than 1
    arcweights = [e[2]["weight"] for e in G.edges.data() if "weight" in e[2]]
    numweights = len(arcweights)
    arcweights = set(arcweights)
    if any(w < 1 for w in arcweights):
        raise nx.NetworkXError(
            "Graph contains arcs with negative or zero weights,"
            " or weights lower than 1. Weights must be >= 1."
        )
    if numweights != len(G.edges):
        print(
            "WARNING: weights are not specified for all arcs."
            " Each arc must have a weight >= 1.\n"
            "Missing weights are automatically set equal to 1."
        )
        for u, v, data in G.edges(data=True):
            if "weight" not in data:
                data["weight"] = 1

    # Sum weights of all arcs
    totalWEI = 0
    for u, v, data in G.edges(data=True):
        totalWEI += data["weight"]

    n1 = nx.number_of_nodes(G) - 1

    # Calculate degree and weighted degree, taking alpha into account
    if type(G) == nx.Graph:
        deg = dict(nx.degree(G))
        indeg = outdeg = wei_insum_alpha_list = wei_outsum_alpha_list = np.nan

        # Calculate weighted degree, taking alpha into account
        # case of different alphas for each metric
        if len(set(alphalist)) != 1:
            wei_sum_alpha_list = [0, 0]
            for a in alphalist[2:4]:  # Only needed for D3 and D4
                if a != 1:
                    wei_sum_alpha = {}
                    for node in G.nodes():
                        wei_sum_alpha[node] = sum(
                            [
                                e[2]["weight"] ** a
                                for e in list(G.edges(node, data=True))
                            ]
                        )
                else:
                    wei_sum_alpha = dict(nx.degree(G, weight="weight"))

                wei_sum_alpha_list.append(wei_sum_alpha)
            wei_sum_alpha_list += [0]
        else:
            if alphalist[0] != 1:
                wei_sum_alpha = {}
                for node in G.nodes():
                    wei_sum_alpha[node] = sum(
                        [
                            e[2]["weight"] ** alphalist[0]
                            for e in list(G.edges(node, data=True))
                        ]
                    )
            else:
                wei_sum_alpha = dict(nx.degree(G, weight="weight"))

            wei_sum_alpha_list = (
                [0, 0] + [wei_sum_alpha] * 2 + [0]
            )  # Only needed for D3 and D4

    elif type(G) == nx.DiGraph:
        deg = wei_sum_alpha_list = np.nan
        indeg = dict(G.in_degree())
        outdeg = dict(G.out_degree())

        if len(set(alphalist)) != 1:
            wei_insum_alpha_list = [0, 0]
            wei_outsum_alpha_list = [0, 0]
            for a in alphalist[2:4]:
                if a != 1:
                    wei_outsum_alpha = {}
                    wei_insum_alpha = {}
                    for node in G.nodes():
                        wei_outsum_alpha[node] = sum(
                            [
                                e[2]["weight"] ** a
                                for e in list(G.out_edges(node, data=True))
                            ]
                        )
                        wei_insum_alpha[node] = sum(
                            [
                                e[2]["weight"] ** a
                                for e in list(G.in_edges(node, data=True))
                            ]
                        )
                else:
                    wei_insum_alpha = dict(G.in_degree(weight="weight"))
                    wei_outsum_alpha = dict(G.out_degree(weight="weight"))

                wei_insum_alpha_list.append(wei_insum_alpha)
                wei_outsum_alpha_list.append(wei_outsum_alpha)

            wei_insum_alpha_list += [0]
            wei_outsum_alpha_list += [0]
        else:
            if alphalist[0] != 1:
                wei_outsum_alpha = {}
                wei_insum_alpha = {}
                for node in G.nodes():
                    wei_outsum_alpha[node] = sum(
                        [
                            e[2]["weight"] ** alphalist[0]
                            for e in list(G.out_edges(node, data=True))
                        ]
                    )
                    wei_insum_alpha[node] = sum(
                        [
                            e[2]["weight"] ** alphalist[0]
                            for e in list(G.in_edges(node, data=True))
                        ]
                    )
            else:
                wei_insum_alpha = dict(G.in_degree(weight="weight"))
                wei_outsum_alpha = dict(G.out_degree(weight="weight"))

            wei_insum_alpha_list = [0, 0] + [wei_insum_alpha] * 2 + [0]
            wei_outsum_alpha_list = [0, 0] + [wei_outsum_alpha] * 2 + [0]

    # Calculate max and min arc weight
    if G.number_of_edges() > 0:
        hasedges = True
        maxwij = max(dict(G.edges).items(),
                     key=lambda x: x[1]["weight"])[1]["weight"]
        minwij = min(dict(G.edges).items(),
                     key=lambda x: x[1]["weight"])[1]["weight"]
    else:
        print(
            "Graph has no edges (remember that loops have been removed)."
            "The function will return all zeros, regardless of normalizaiton."
        )
        hasedges = False
        maxwij = np.nan
        minwij = np.nan

    return (
        G,
        n1,
        deg,
        indeg,
        outdeg,
        wei_insum_alpha_list,
        wei_outsum_alpha_list,
        wei_sum_alpha_list,
        totalWEI,
        maxwij,
        minwij,
        hasedges,
    )


def distinctiveness(G, alpha=1, normalize=False):
    r"""Compute the Distinctiveness Centrality for the graph `G`.

    Distinctiveness Centrality is a set of 5 network metrics
    that attribute larger importance to distinctive connections.
    The are five formulas that can be used
    to calculate Distinctiveness Centrality.
    This function calculates them all
    and provides results as a list of dictionaries.

    Parameters
    ----------
    G : graph
        A Networkx Graph or DiGraph. Multigraphs are automatically
        transformed into graphs, by summing arc weights.
        Please note that each arc is expected to have a weight attribute,
        otherwise each missing weight will be considered equal to 1.
        Weights have to be >= 1.

    alpha : float or list, optional (default=1)
        alpha must be a number greater or equal to 1.
        It represents the value of the alpha parameter used in
        the generalized formulas of distinctiveness centrality.
        If one value is provided it will be used for all the five metrics.
        Alternatively, alpha can be a list of five numbers,
        used to specify different coefficients
        for the different metrics (e.g. alpha = [1, 2, 1, 1, 5]).

    normalize : bool, optional (default=False)
            Normalize can be set to True,
            to obtain normalized scores for each metric,
            considering upper and lower bounds. Loose upper
            and lower bounds are used for D3.
            Normalization is only carried out for undirected
            graph measures.

    Returns
    -------
    nodes : dictionary
        A dictionary with 15 keys, each one indicating one distinctiveness
        centrality metric. The value of each key is a dictionary of nodes,
        with distinctiveness scores. Because distinctiveness can be calculated
        using five different formulas, the first 5 keys are named as D1, D2,
        D3, D4 and D5. These measures are calculated if a Graph is
        given as input (otherwise nans will be generated).
        The other 10 measures are for the directed networks and will
        be available if a DiGraph is given as input
        (otherwise nans will be generated).
        These are: D1_in, D2_in, D3_in, D4_in,
        D5_in, D1_out, D2_out, D3_out, D4_out and D5_out.

    Examples
    --------
    >>> G = nx.star_graph(4)
    >>> d1 = nx.distinctiveness(G, alpha = 1, normalize = False)["D1"]
    WARNING: weights are not specified for all arcs. Each arc must have a weight >= 1.
    Missing weights are automatically set equal to 1.
    >>> for n, c in sorted(d1.items()):
    ...    print(f"{n} {c:.2f}")
    0 2.41
    1 0.00
    2 0.00
    3 0.00
    4 0.00

    References
    ----------
    Fronzetti Colladon, A., & Naldi, M. (2020).
     Distinctiveness Centrality in Social Networks.
     PLoS ONE, 15(5), e0233276. <https://doi.org/10.1371/journal.pone.0233276>

    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError("distinctiveness requires NumPy ",
                          "http://scipy.org/")

    if isinstance(alpha, list) and len(alpha) == 5:
        alphalist = alpha
    elif isinstance(alpha, (int, float)):
        alphalist = [alpha] * 5
    else:
        raise nx.NetworkXError(
            "Error in the choice of alpha."
            " Please specify a single number or a list of 5 values."
        )
        return np.nan

    if any(a < 1 for a in alphalist):
        print(
            "WARNING. Alpha should be >= 1,"
            " except you exactly know what you are doing."
        )
        if normalize is True:
            print(
                "For alpha < 1 normalization is not carried out."
                " This will be deactivated for all metrics."
            )
            normalize = False

    (
        G,
        n1,
        deg,
        indeg,
        outdeg,
        wei_insum_alpha_list,
        wei_outsum_alpha_list,
        wei_sum_alpha_list,
        totalWEI,
        maxwij,
        minwij,
        hasedges,
    ) = g_preprocess(G, alpha=alpha)

    if not hasedges:
        normalize = False

    Glist = list(G.nodes)

    # Define max of all metrics
    if normalize is True:
        print(
            "WARNING. Normalization of D3 is"
            " carried out using loose upper and lower bounds."
        )

        D1max = np.log10(n1) * n1 * maxwij
        D1min = (1 - alphalist[0]) * maxwij * np.log10(n1) * n1

        D2max = np.log10(n1) * n1
        D2min = (1 - alphalist[1]) * np.log10(n1) * n1

        if type(G) == nx.Graph:
            D3max = np.log10(maxwij * (n1 + 1) * n1 * 0.5) * maxwij * n1
        elif type(G) == nx.DiGraph:
            D3max = np.log10(maxwij * (n1 + 1) * n1) * maxwij * n1

        threshold = (n1 - 1) * (maxwij ** alphalist[2] - maxwij)
        if (minwij - 1) > threshold:
            D3min = 0  # considers isolates
        else:
            D3min = (
                n1
                * maxwij
                * np.log10(
                    ((n1 - 1) * maxwij + minwij)
                    / ((n1 - 1) * (maxwij) ** alphalist[2] + 1)
                )
            )

        D4max = n1 * maxwij
        D4min = 0  # considers isolates

        D5max = n1
        D5min = 0  # considers isolates # 1/(n1**alphalist[4])
    else:
        D1max = D2max = D3max = D4max = D5max = 1
        D1min = D2min = D3min = D4min = D5min = 0

    # Computes Distinctiveness Centrality, all 5 metrics
    if type(G) == nx.Graph:
        # Set keys to zero for all nodes (to take isolates into account)
        d1, d2, d3, d4, d5 = (
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
        )
        d1_in = np.nan
        d2_in = np.nan
        d3_in = np.nan
        d4_in = np.nan
        d5_in = np.nan
        d1_out = np.nan
        d2_out = np.nan
        d3_out = np.nan
        d4_out = np.nan
        d5_out = np.nan

        for u, v, data in G.edges(data=True):
            d1[u] += data["weight"] * np.log10(n1 / deg[v] ** alphalist[0])
            d1[v] += data["weight"] * np.log10(n1 / deg[u] ** alphalist[0])

            d2[u] += 1 * np.log10(n1 / deg[v] ** alphalist[1])
            d2[v] += 1 * np.log10(n1 / deg[u] ** alphalist[1])

            d3[u] += data["weight"] * np.log10(
                totalWEI
                / (wei_sum_alpha_list[2][v]
                   - data["weight"] ** alphalist[2] + 1)
            )
            d3[v] += data["weight"] * np.log10(
                totalWEI
                / (wei_sum_alpha_list[2][u]
                   - data["weight"] ** alphalist[2] + 1)
            )

            d4[u] += data["weight"] * (
                data["weight"] ** alphalist[3] / wei_sum_alpha_list[3][v]
            )
            d4[v] += data["weight"] * (
                data["weight"] ** alphalist[3] / wei_sum_alpha_list[3][u]
            )

            d5[u] += 1 * (1 / deg[v] ** alphalist[4])
            d5[v] += 1 * (1 / deg[u] ** alphalist[4])

        if normalize is True:
            d1 = {k: (v - D1min) / (D1max - D1min) for k, v in d1.items()}
            d2 = {k: (v - D2min) / (D2max - D2min) for k, v in d2.items()}
            d3 = {k: (v - D3min) / (D3max - D3min) for k, v in d3.items()}
            d4 = {k: (v - D4min) / (D4max - D4min) for k, v in d4.items()}
            d5 = {k: (v - D5min) / (D5max - D5min) for k, v in d5.items()}

    elif type(G) == nx.DiGraph:
        # Set keys to zero for all nodes
        # (to take isolates into account and nodes with zero in- or out-degree)
        (d1_in, d2_in, d3_in, d4_in, d5_in, d1_out,
         d2_out, d3_out, d4_out, d5_out) = (
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
            dict.fromkeys(Glist, 0),
        )
        d1 = d2 = d3 = d4 = d5 = np.nan

        for u, v, data in G.edges(data=True):
            d1_in[v] += data["weight"] * np.log10(n1
                                                  / outdeg[u] ** alphalist[0])
            d1_out[u] += data["weight"] * np.log10(n1
                                                   / indeg[v] ** alphalist[0])

            d2_in[v] += 1 * np.log10(n1 / outdeg[u] ** alphalist[1])
            d2_out[u] += 1 * np.log10(n1 / indeg[v] ** alphalist[1])

            d3_in[v] += data["weight"] * np.log10(
                totalWEI
                / (wei_outsum_alpha_list[2][u]
                   - data["weight"] ** alphalist[2] + 1)
            )
            d3_out[u] += data["weight"] * np.log10(
                totalWEI
                / (wei_insum_alpha_list[2][v]
                   - data["weight"] ** alphalist[2] + 1)
            )

            d4_in[v] += data["weight"] * (
                data["weight"] ** alphalist[3] / wei_outsum_alpha_list[3][u]
            )
            d4_out[u] += data["weight"] * (
                data["weight"] ** alphalist[3] / wei_insum_alpha_list[3][v]
            )

            d5_in[v] += 1 * (1 / outdeg[u] ** alphalist[4])
            d5_out[u] += 1 * (1 / indeg[v] ** alphalist[4])

        if normalize is True:
            print("Normalization is only carried out for undirected graph metrics.")
            # d1_in = {k: (v - D1min) / (D1max - D1min)
            #          for k, v in d1_in.items()}
            # d2_in = {k: (v - D2min) / (D2max - D2min)
            #          for k, v in d2_in.items()}
            # d3_in = {k: (v - D3min) / (D3max - D3min)
            #          for k, v in d3_in.items()}
            # d4_in = {k: (v - D4min) / (D4max - D4min)
            #          for k, v in d4_in.items()}
            # d5_in = {k: (v - D5min) / (D5max - D5min)
            #          for k, v in d5_in.items()}

            # d1_out = {k: (v - D1min) / (D1max - D1min)
            #           for k, v in d1_out.items()}
            # d2_out = {k: (v - D2min) / (D2max - D2min)
            #           for k, v in d2_out.items()}
            # d3_out = {k: (v - D3min) / (D3max - D3min)
            #           for k, v in d3_out.items()}
            # d4_out = {k: (v - D4min) / (D4max - D4min)
            #           for k, v in d4_out.items()}
            # d5_out = {k: (v - D5min) / (D5max - D5min)
            #           for k, v in d5_out.items()}

    DC = {
        "D1": d1,
        "D2": d2,
        "D3": d3,
        "D4": d4,
        "D5": d5,
        "D1_in": d1_in,
        "D2_in": d2_in,
        "D3_in": d3_in,
        "D4_in": d4_in,
        "D5_in": d5_in,
        "D1_out": d1_out,
        "D2_out": d2_out,
        "D3_out": d3_out,
        "D4_out": d4_out,
        "D5_out": d5_out,
    }

    return DC
