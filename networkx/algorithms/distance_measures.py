"""Graph diameter, radius, eccentricity and other properties."""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = [
    "extrema_bounding",
    "eccentricity",
    "diameter",
    "radius",
    "periphery",
    "center",
    "barycenter",
    "resistance_distance",
    "hamming_distance",
    "generalized_hamming_distance",
    "2d_generalized_hamming_distance",
    "diversity",
]


def extrema_bounding(G, compute="diameter"):
    """Compute requested extreme distance metric of undirected graph G

    .. deprecated:: 2.8

       extrema_bounding is deprecated and will be removed in NetworkX 3.0.
       Use the corresponding distance measure with the `usebounds=True` option
       instead.

    Computation is based on smart lower and upper bounds, and in practice
    linear in the number of nodes, rather than quadratic (except for some
    border cases such as complete graphs or circle shaped graphs).

    Parameters
    ----------
    G : NetworkX graph
       An undirected graph

    compute : string denoting the requesting metric
       "diameter" for the maximal eccentricity value,
       "radius" for the minimal eccentricity value,
       "periphery" for the set of nodes with eccentricity equal to the diameter,
       "center" for the set of nodes with eccentricity equal to the radius,
       "eccentricities" for the maximum distance from each node to all other nodes in G

    Returns
    -------
    value : value of the requested metric
       int for "diameter" and "radius" or
       list of nodes for "center" and "periphery" or
       dictionary of eccentricity values keyed by node for "eccentricities"

    Raises
    ------
    NetworkXError
        If the graph consists of multiple components
    ValueError
        If `compute` is not one of "diameter", "radius", "periphery", "center", or "eccentricities".
    Notes
    -----
    This algorithm was proposed in the following papers:

    F.W. Takes and W.A. Kosters, Determining the Diameter of Small World
    Networks, in Proceedings of the 20th ACM International Conference on
    Information and Knowledge Management (CIKM 2011), pp. 1191-1196, 2011.
    doi: https://doi.org/10.1145/2063576.2063748

    F.W. Takes and W.A. Kosters, Computing the Eccentricity Distribution of
    Large Graphs, Algorithms 6(1): 100-118, 2013.
    doi: https://doi.org/10.3390/a6010100

    M. Borassi, P. Crescenzi, M. Habib, W.A. Kosters, A. Marino and F.W. Takes,
    Fast Graph Diameter and Radius BFS-Based Computation in (Weakly Connected)
    Real-World Graphs, Theoretical Computer Science 586: 59-80, 2015.
    doi: https://doi.org/10.1016/j.tcs.2015.02.033
    """
    import warnings

    msg = "extrema_bounding is deprecated and will be removed in networkx 3.0\n"
    # NOTE: _extrema_bounding does input checking, so it is skipped here
    if compute in {"diameter", "radius", "periphery", "center"}:
        msg += f"Use nx.{compute}(G, usebounds=True) instead."
    if compute == "eccentricities":
        msg += f"Use nx.eccentricity(G) instead."
    warnings.warn(msg, DeprecationWarning, stacklevel=2)

    return _extrema_bounding(G, compute=compute)


def _extrema_bounding(G, compute="diameter"):
    """Compute requested extreme distance metric of undirected graph G

    Computation is based on smart lower and upper bounds, and in practice
    linear in the number of nodes, rather than quadratic (except for some
    border cases such as complete graphs or circle shaped graphs).

    Parameters
    ----------
    G : NetworkX graph
       An undirected graph

    compute : string denoting the requesting metric
       "diameter" for the maximal eccentricity value,
       "radius" for the minimal eccentricity value,
       "periphery" for the set of nodes with eccentricity equal to the diameter,
       "center" for the set of nodes with eccentricity equal to the radius,
       "eccentricities" for the maximum distance from each node to all other nodes in G

    Returns
    -------
    value : value of the requested metric
       int for "diameter" and "radius" or
       list of nodes for "center" and "periphery" or
       dictionary of eccentricity values keyed by node for "eccentricities"

    Raises
    ------
    NetworkXError
        If the graph consists of multiple components
    ValueError
        If `compute` is not one of "diameter", "radius", "periphery", "center", or "eccentricities".
    Notes
    -----
    This algorithm was proposed in the following papers:

    F.W. Takes and W.A. Kosters, Determining the Diameter of Small World
    Networks, in Proceedings of the 20th ACM International Conference on
    Information and Knowledge Management (CIKM 2011), pp. 1191-1196, 2011.
    doi: https://doi.org/10.1145/2063576.2063748

    F.W. Takes and W.A. Kosters, Computing the Eccentricity Distribution of
    Large Graphs, Algorithms 6(1): 100-118, 2013.
    doi: https://doi.org/10.3390/a6010100

    M. Borassi, P. Crescenzi, M. Habib, W.A. Kosters, A. Marino and F.W. Takes,
    Fast Graph Diameter and Radius BFS-Based Computation in (Weakly Connected)
    Real-World Graphs, Theoretical Computer Science 586: 59-80, 2015.
    doi: https://doi.org/10.1016/j.tcs.2015.02.033
    """

    # init variables
    degrees = dict(G.degree())  # start with the highest degree node
    minlowernode = max(degrees, key=degrees.get)
    N = len(degrees)  # number of nodes
    # alternate between smallest lower and largest upper bound
    high = False
    # status variables
    ecc_lower = dict.fromkeys(G, 0)
    ecc_upper = dict.fromkeys(G, N)
    candidates = set(G)

    # (re)set bound extremes
    minlower = N
    maxlower = 0
    minupper = N
    maxupper = 0

    # repeat the following until there are no more candidates
    while candidates:
        if high:
            current = maxuppernode  # select node with largest upper bound
        else:
            current = minlowernode  # select node with smallest lower bound
        high = not high

        # get distances from/to current node and derive eccentricity
        dist = dict(nx.single_source_shortest_path_length(G, current))
        if len(dist) != N:
            msg = "Cannot compute metric because graph is not connected."
            raise nx.NetworkXError(msg)
        current_ecc = max(dist.values())

        # print status update
        #        print ("ecc of " + str(current) + " (" + str(ecc_lower[current]) + "/"
        #        + str(ecc_upper[current]) + ", deg: " + str(dist[current]) + ") is "
        #        + str(current_ecc))
        #        print(ecc_upper)

        # (re)set bound extremes
        maxuppernode = None
        minlowernode = None

        # update node bounds
        for i in candidates:
            # update eccentricity bounds
            d = dist[i]
            ecc_lower[i] = low = max(ecc_lower[i], max(d, (current_ecc - d)))
            ecc_upper[i] = upp = min(ecc_upper[i], current_ecc + d)

            # update min/max values of lower and upper bounds
            minlower = min(ecc_lower[i], minlower)
            maxlower = max(ecc_lower[i], maxlower)
            minupper = min(ecc_upper[i], minupper)
            maxupper = max(ecc_upper[i], maxupper)

        # update candidate set
        if compute == "diameter":
            ruled_out = {
                i
                for i in candidates
                if ecc_upper[i] <= maxlower and 2 * ecc_lower[i] >= maxupper
            }
        elif compute == "radius":
            ruled_out = {
                i
                for i in candidates
                if ecc_lower[i] >= minupper and ecc_upper[i] + 1 <= 2 * minlower
            }
        elif compute == "periphery":
            ruled_out = {
                i
                for i in candidates
                if ecc_upper[i] < maxlower
                and (maxlower == maxupper or ecc_lower[i] > maxupper)
            }
        elif compute == "center":
            ruled_out = {
                i
                for i in candidates
                if ecc_lower[i] > minupper
                and (minlower == minupper or ecc_upper[i] + 1 < 2 * minlower)
            }
        elif compute == "eccentricities":
            ruled_out = set()
        else:
            msg = "compute must be one of 'diameter', 'radius', 'periphery', 'center', 'eccentricities'"
            raise ValueError(msg)

        ruled_out.update(i for i in candidates if ecc_lower[i] == ecc_upper[i])
        candidates -= ruled_out

        #        for i in ruled_out:
        #            print("removing %g: ecc_u: %g maxl: %g ecc_l: %g maxu: %g"%
        #                    (i,ecc_upper[i],maxlower,ecc_lower[i],maxupper))
        #        print("node %g: ecc_u: %g maxl: %g ecc_l: %g maxu: %g"%
        #                    (4,ecc_upper[4],maxlower,ecc_lower[4],maxupper))
        #        print("NODE 4: %g"%(ecc_upper[4] <= maxlower))
        #        print("NODE 4: %g"%(2 * ecc_lower[4] >= maxupper))
        #        print("NODE 4: %g"%(ecc_upper[4] <= maxlower
        #                            and 2 * ecc_lower[4] >= maxupper))

        # updating maxuppernode and minlowernode for selection in next round
        for i in candidates:
            if (
                minlowernode is None
                or (
                    ecc_lower[i] == ecc_lower[minlowernode]
                    and degrees[i] > degrees[minlowernode]
                )
                or (ecc_lower[i] < ecc_lower[minlowernode])
            ):
                minlowernode = i

            if (
                maxuppernode is None
                or (
                    ecc_upper[i] == ecc_upper[maxuppernode]
                    and degrees[i] > degrees[maxuppernode]
                )
                or (ecc_upper[i] > ecc_upper[maxuppernode])
            ):
                maxuppernode = i

        # print status update
    #        print (" min=" + str(minlower) + "/" + str(minupper) +
    #        " max=" + str(maxlower) + "/" + str(maxupper) +
    #        " candidates: " + str(len(candidates)))
    #        print("cand:",candidates)
    #        print("ecc_l",ecc_lower)
    #        print("ecc_u",ecc_upper)
    #        wait = input("press Enter to continue")

    # return the correct value of the requested metric
    if compute == "diameter":
        return maxlower
    elif compute == "radius":
        return minupper
    elif compute == "periphery":
        p = [v for v in G if ecc_lower[v] == maxlower]
        return p
    elif compute == "center":
        c = [v for v in G if ecc_upper[v] == minupper]
        return c
    elif compute == "eccentricities":
        return ecc_lower
    return None


def eccentricity(G, v=None, sp=None):
    """Returns the eccentricity of nodes in G.

    The eccentricity of a node v is the maximum distance from v to
    all other nodes in G.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    v : node, optional
       Return value of specified node

    sp : dict of dicts, optional
       All pairs shortest path lengths as a dictionary of dictionaries

    Returns
    -------
    ecc : dictionary
       A dictionary of eccentricity values keyed by node.
    """
    #    if v is None:                # none, use entire graph
    #        nodes=G.nodes()
    #    elif v in G:               # is v a single node
    #        nodes=[v]
    #    else:                      # assume v is a container of nodes
    #        nodes=v
    order = G.order()

    e = {}
    for n in G.nbunch_iter(v):
        if sp is None:
            length = nx.single_source_shortest_path_length(G, n)
            L = len(length)
        else:
            try:
                length = sp[n]
                L = len(length)
            except TypeError as err:
                raise nx.NetworkXError('Format of "sp" is invalid.') from err
        if L != order:
            if G.is_directed():
                msg = (
                    "Found infinite path length because the digraph is not"
                    " strongly connected"
                )
            else:
                msg = "Found infinite path length because the graph is not" " connected"
            raise nx.NetworkXError(msg)

        e[n] = max(length.values())

    if v in G:
        return e[v]  # return single value
    else:
        return e


def diameter(G, e=None, usebounds=False):
    """Returns the diameter of the graph G.

    The diameter is the maximum eccentricity.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    d : integer
       Diameter of graph

    See Also
    --------
    eccentricity
    """
    if usebounds is True and e is None and not G.is_directed():
        return _extrema_bounding(G, compute="diameter")
    if e is None:
        e = eccentricity(G)
    return max(e.values())


def periphery(G, e=None, usebounds=False):
    """Returns the periphery of the graph G.

    The periphery is the set of nodes with eccentricity equal to the diameter.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    p : list
       List of nodes in periphery

    See Also
    --------
    barycenter
    center
    """
    if usebounds is True and e is None and not G.is_directed():
        return _extrema_bounding(G, compute="periphery")
    if e is None:
        e = eccentricity(G)
    diameter = max(e.values())
    p = [v for v in e if e[v] == diameter]
    return p


def radius(G, e=None, usebounds=False):
    """Returns the radius of the graph G.

    The radius is the minimum eccentricity.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    r : integer
       Radius of graph
    """
    if usebounds is True and e is None and not G.is_directed():
        return _extrema_bounding(G, compute="radius")
    if e is None:
        e = eccentricity(G)
    return min(e.values())


def center(G, e=None, usebounds=False):
    """Returns the center of the graph G.

    The center is the set of nodes with eccentricity equal to radius.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    c : list
       List of nodes in center

    See Also
    --------
    barycenter
    periphery
    """
    if usebounds is True and e is None and not G.is_directed():
        return _extrema_bounding(G, compute="center")
    if e is None:
        e = eccentricity(G)
    radius = min(e.values())
    p = [v for v in e if e[v] == radius]
    return p


def barycenter(G, weight=None, attr=None, sp=None):
    r"""Calculate barycenter of a connected graph, optionally with edge weights.

    The :dfn:`barycenter` a
    :func:`connected <networkx.algorithms.components.is_connected>` graph
    :math:`G` is the subgraph induced by the set of its nodes :math:`v`
    minimizing the objective function

    .. math::

        \sum_{u \in V(G)} d_G(u, v),

    where :math:`d_G` is the (possibly weighted) :func:`path length
    <networkx.algorithms.shortest_paths.generic.shortest_path_length>`.
    The barycenter is also called the :dfn:`median`. See [West01]_, p. 78.

    Parameters
    ----------
    G : :class:`networkx.Graph`
        The connected graph :math:`G`.
    weight : :class:`str`, optional
        Passed through to
        :func:`~networkx.algorithms.shortest_paths.generic.shortest_path_length`.
    attr : :class:`str`, optional
        If given, write the value of the objective function to each node's
        `attr` attribute. Otherwise do not store the value.
    sp : dict of dicts, optional
       All pairs shortest path lengths as a dictionary of dictionaries

    Returns
    -------
    list
        Nodes of `G` that induce the barycenter of `G`.

    Raises
    ------
    NetworkXNoPath
        If `G` is disconnected. `G` may appear disconnected to
        :func:`barycenter` if `sp` is given but is missing shortest path
        lengths for any pairs.
    ValueError
        If `sp` and `weight` are both given.

    See Also
    --------
    center
    periphery
    """
    if sp is None:
        sp = nx.shortest_path_length(G, weight=weight)
    else:
        sp = sp.items()
        if weight is not None:
            raise ValueError("Cannot use both sp, weight arguments together")
    smallest, barycenter_vertices, n = float("inf"), [], len(G)
    for v, dists in sp:
        if len(dists) < n:
            raise nx.NetworkXNoPath(
                f"Input graph {G} is disconnected, so every induced subgraph "
                "has infinite barycentricity."
            )
        barycentricity = sum(dists.values())
        if attr is not None:
            G.nodes[v][attr] = barycentricity
        if barycentricity < smallest:
            smallest = barycentricity
            barycenter_vertices = [v]
        elif barycentricity == smallest:
            barycenter_vertices.append(v)
    return barycenter_vertices


def _count_lu_permutations(perm_array):
    """Counts the number of permutations in SuperLU perm_c or perm_r"""
    perm_cnt = 0
    arr = perm_array.tolist()
    for i in range(len(arr)):
        if i != arr[i]:
            perm_cnt += 1
            n = arr.index(i)
            arr[n] = arr[i]
            arr[i] = i

    return perm_cnt


@not_implemented_for("directed")
def resistance_distance(G, nodeA, nodeB, weight=None, invert_weight=True):
    """Returns the resistance distance between node A and node B on graph G.

    The resistance distance between two nodes of a graph is akin to treating
    the graph as a grid of resistorses with a resistance equal to the provided
    weight.

    If weight is not provided, then a weight of 1 is used for all edges.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    nodeA : node
      A node within graph G.

    nodeB : node
      A node within graph G, exclusive of Node A.

    weight : string or None, optional (default=None)
       The edge data key used to compute the resistance distance.
       If None, then each edge has weight 1.

    invert_weight : boolean (default=True)
        Proper calculation of resistance distance requires building the
        Laplacian matrix with the reciprocal of the weight. Not required
        if the weight is already inverted. Weight cannot be zero.

    Returns
    -------
    rd : float
       Value of effective resistance distance

    Notes
    -----
    Overview discussion:
    * https://en.wikipedia.org/wiki/Resistance_distance
    * http://mathworld.wolfram.com/ResistanceDistance.html

    Additional details:
    Vaya Sapobi Samui Vos, “Methods for determining the effective resistance,” M.S.,
    Mathematisch Instituut, Universiteit Leiden, Leiden, Netherlands, 2016
    Available: `Link to thesis <https://www.universiteitleiden.nl/binaries/content/assets/science/mi/scripties/master/vos_vaya_master.pdf>`_
    """
    import numpy as np
    import scipy as sp
    import scipy.sparse.linalg  # call as sp.sparse.linalg

    if not nx.is_connected(G):
        msg = "Graph G must be strongly connected."
        raise nx.NetworkXError(msg)
    elif nodeA not in G:
        msg = "Node A is not in graph G."
        raise nx.NetworkXError(msg)
    elif nodeB not in G:
        msg = "Node B is not in graph G."
        raise nx.NetworkXError(msg)
    elif nodeA == nodeB:
        msg = "Node A and Node B cannot be the same."
        raise nx.NetworkXError(msg)

    G = G.copy()
    node_list = list(G)

    if invert_weight and weight is not None:
        if G.is_multigraph():
            for (u, v, k, d) in G.edges(keys=True, data=True):
                d[weight] = 1 / d[weight]
        else:
            for (u, v, d) in G.edges(data=True):
                d[weight] = 1 / d[weight]
    # Replace with collapsing topology or approximated zero?

    # Using determinants to compute the effective resistance is more memory
    # efficent than directly calculating the psuedo-inverse
    L = nx.laplacian_matrix(G, node_list, weight=weight).asformat("csc")
    indices = list(range(L.shape[0]))
    # w/ nodeA removed
    indices.remove(node_list.index(nodeA))
    L_a = L[indices, :][:, indices]
    # Both nodeA and nodeB removed
    indices.remove(node_list.index(nodeB))
    L_ab = L[indices, :][:, indices]

    # Factorize Laplacian submatrixes and extract diagonals
    # Order the diagonals to minimize the likelihood over overflows
    # during computing the determinant
    lu_a = sp.sparse.linalg.splu(L_a, options=dict(SymmetricMode=True))
    LdiagA = lu_a.U.diagonal()
    LdiagA_s = np.product(np.sign(LdiagA)) * np.product(lu_a.L.diagonal())
    LdiagA_s *= (-1) ** _count_lu_permutations(lu_a.perm_r)
    LdiagA_s *= (-1) ** _count_lu_permutations(lu_a.perm_c)
    LdiagA = np.absolute(LdiagA)
    LdiagA = np.sort(LdiagA)

    lu_ab = sp.sparse.linalg.splu(L_ab, options=dict(SymmetricMode=True))
    LdiagAB = lu_ab.U.diagonal()
    LdiagAB_s = np.product(np.sign(LdiagAB)) * np.product(lu_ab.L.diagonal())
    LdiagAB_s *= (-1) ** _count_lu_permutations(lu_ab.perm_r)
    LdiagAB_s *= (-1) ** _count_lu_permutations(lu_ab.perm_c)
    LdiagAB = np.absolute(LdiagAB)
    LdiagAB = np.sort(LdiagAB)

    # Calculate the ratio of determinant, rd = det(L_ab)/det(L_a)
    Ldet = np.product(np.divide(np.append(LdiagAB, [1]), LdiagA))
    rd = Ldet * LdiagAB_s / LdiagA_s

    return rd


def hamming_distance(G, H):
    """Return the Hamming distance between two graphs.

    The Hamming distance is the number of edges contained in one
    but not the other graph.

    Parameters
    ----------
    G : NetworkX graph
        First Graph
    H : NetworkX graph
        Second Graph
    Returns
    -------
    count : integer
      The hamming distance.
    """
    count = 0
    for e in G.edges():
        if not H.has_edge(*e):
            count += 1
    for e in H.edges():
        if not G.has_edge(*e):
            count += 1
    return count


def generalized_hamming_distance(G, H, no_edge_cost=0.5, default=0):
    """Return the Generalized Hamming distance between two (possibly directed and weighted) graphs.
    The Generalized Hamming distance is the difference in weights between each of the edges contained in two graphs, with a special cost for edges that exist in one of the graphs, but not the other.
    Parameters
    ----------
    G, H : NetworkX graph/digraph (with weighted edges, where the relevant edge attribute is "weight")
       The graphs to be compared
    no_edge_cost : float
    the extra cost that is attributed to comparing an edge that exists in one graph with a missing edge in the other graph.
    Returns
    -------
    count : float
      The generalized hamming distance.
    """

    count = 0
    for e in G.edges():
        try:
            if H.has_edge(*e):
                count += abs(
                    nx.get_edge_attributes(G, "weight")[e]
                    - nx.get_edge_attributes(H, "weight")[e]
                )

            else:
                count += abs(nx.get_edge_attributes(G, "weight")[e]) + no_edge_cost
        except:
            raise ValueError("%s does not have a weight!" % str(e))

    # And now for the edges that are in H but not in G:
    for e in H.edges():
        if not G.has_edge(*e):
            try:
                count += abs(nx.get_edge_attributes(H, "weight")[e]) + no_edge_cost
            except:
                raise ValueError("%s does not have a weight!" % str(e))

    return count


def two_d_generalized_hamming_distance(G, H, no_edge_params=(0, 2)):
    """Return the Two-Dimensional Generalized Hamming distance between two (possibly directed) graphs, where each link has information on two dimensions (interpreted, for example, as mean and variance).
    The Two-Dimensional Generalized Hamming distance is the summation of Euclidean distances between two dimensional weights for each of the edges contained in two graphs, with assumed parameters for edges that do not exist in a graph, in order to compare these non-existing edges with existing ones in the other graph.
    Parameters
    ----------
    G, H : NetworkX graph/digraph (with weighted edges, where the relevant edge attribute is "weight")
       The graphs to be compared
    no_edge_params : tuple of two floats or integers
    the assumed two dimensional parameter that is used to compare a non-existing edge for one graph with an existing one in the other graph.
    Returns
    -------
    count : float
      The generalized hamming distance.
    """

    from numpy import sqrt

    count = 0
    for e in G.edges():
        if H.has_edge(*e):
            try:
                count += sqrt(
                    (
                        nx.get_edge_attributes(G, "mu")[e]
                        - nx.get_edge_attributes(H, "mu")[e]
                    )
                    ** 2
                    + (
                        nx.get_edge_attributes(G, "sigma")[e]
                        - nx.get_edge_attributes(H, "sigma")[e]
                    )
                    ** 2
                )

            except:
                raise ValueError("%s does not have a mu or a sigma!" % str(e))
        else:
            try:
                count += sqrt(
                    (nx.get_edge_attributes(G, "mu")[e] - no_edge_params[0]) ** 2
                    + (nx.get_edge_attributes(G, "sigma")[e] - no_edge_params[1]) ** 2
                )
            except:
                raise ValueError("%s does not have a mu or a sigma!" % str(e))

    # And now for the edges that are in H but not in G:
    for e in H.edges():
        if not G.has_edge(*e):
            try:
                count += sqrt(
                    (nx.get_edge_attributes(H, "mu")[e] - no_edge_params[0]) ** 2
                    + (nx.get_edge_attributes(H, "sigma")[e] - no_edge_params[1]) ** 2
                )

            except:
                raise ValueError("%s does not have a mu or a sigma!" % str(e))

    return count


# problem with edges not having mu and sigma. Have to attach edges differently!


def diversity(obj_set, distance=two_d_generalized_hamming_distance):
    """Return the Weitzman diversity measure (Weitzman 1992) of a set of objects with a distance function defined over any
    two objects in the set.
    The Diversity of a collection of graphs is calculated and returned, according to the algorithm suggested by Martin Weitzman in 1992.
    Parameters
    ----------
    obj_set : A set containing NetworkX graphs/digraphs or any other objects with a distance metric.
       The set of objects for which the diversity is to be calculated
    distance : a function
    a distance function for any two objects.
    Returns
    -------
    count : float
      The diversity of a collection of objects.
    """

    """
    This function calculates the Weitzman diversity measure (Weitzman 1992) of a set of objects with a distance function defined over any
    two objects in the set.
    """
    S = set()
    divers = 0
    g = obj_set.pop()  # Step1: randomly pick an object from the object set
    S.add(g)
    while obj_set:
        set_distance = min(distance(g, h) for g in S for h in obj_set)
        min_elem = [
            elem
            for elem in obj_set
            if min(distance(elem, g) for g in S) == set_distance
        ].pop()

        S.add(min_elem)  # Step2: add closest member of the object set to the set, S
        obj_set.remove(min_elem)  # and remove it from the object set
        divers += set_distance  # Step3: increment the diversity by the distance between the set S, and the new member.

    # Normalize the diversity by the number of objects:
    # make a distance matrix where the distances don't have to be recalculated (memoization)
    return float(divers) / len(S)
