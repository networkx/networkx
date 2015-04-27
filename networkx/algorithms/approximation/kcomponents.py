""" Fast approximation for k-component structure
"""
#    Copyright (C) 2015 by 
#    Jordi Torrents <jtorrents@milnou.net>
#    All rights reserved.
#    BSD license.
import itertools
import collections

import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import not_implemented_for

from networkx.algorithms.approximation import local_node_connectivity
from networkx.algorithms.connectivity import \
    local_node_connectivity as exact_local_node_connectivity
from networkx.algorithms.connectivity import build_auxiliary_node_connectivity
from networkx.algorithms.flow import build_residual_network


__author__ = """\n""".join(['Jordi Torrents <jtorrents@milnou.net>'])

__all__ = ['k_components']


not_implemented_for('directed')
def k_components(G, min_density=0.95):
    r"""Returns the approximate k-component structure of a graph G.
    
    A `k`-component is a maximal subgraph of a graph G that has, at least, 
    node connectivity `k`: we need to remove at least `k` nodes to break it
    into more components. `k`-components have an inherent hierarchical
    structure because they are nested in terms of connectivity: a connected 
    graph can contain several 2-components, each of which can contain 
    one or more 3-components, and so forth.

    This implementation is based on the fast heuristics to approximate
    the `k`-component sturcture of a graph [1]_. Which, in turn, it is based on
    a fast approximation algorithm for finding good lower bounds of the number 
    of node independent paths between two nodes [2]_.
  
    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    min_density : Float
        Density relaxation treshold. Default value 0.95

    Returns
    -------
    k_components : dict
        Dictionary with connectivity level `k` as key and a list of
        sets of nodes that form a k-component of level `k` as values.
        

    Examples
    --------
    >>> # Petersen graph has 10 nodes and it is triconnected, thus all 
    >>> # nodes are in a single component on all three connectivity levels
    >>> from networkx.algorithms import approximation as apxa
    >>> G = nx.petersen_graph()
    >>> k_components = apxa.k_components(G)
    
    Notes
    -----
    The logic of the approximation algorithm for computing the `k`-component 
    structure [1]_ is based on repeatedly applying simple and fast algorithms 
    for `k`-cores and biconnected components in order to narrow down the 
    number of pairs of nodes over which we have to compute White and Newman's
    approximation algorithm for finding node independent paths [2]_. More
    formally, this algorithm is based on Whitney's theorem, which states 
    an inclusion relation among node connectivity, edge connectivity, and 
    minimum degree for any graph G. This theorem implies that every 
    `k`-component is nested inside a `k`-edge-component, which in turn, 
    is contained in a `k`-core. Thus, this algorithm computes node independent
    paths among pairs of nodes in each biconnected part of each `k`-core,
    and repeats this procedure for each `k` from 3 to the maximal core number 
    of a node in the input graph.

    Because, in practice, many nodes of the core of level `k` inside a 
    bicomponent actually are part of a component of level k, the auxiliary 
    graph needed for the algorithm is likely to be very dense. Thus, we use 
    a complement graph data structure (see `AntiGraph`) to save memory. 
    AntiGraph only stores information of the edges that are *not* present 
    in the actual auxiliary graph. When applying algorithms to this 
    complement graph data structure, it behaves as if it were the dense 
    version.

    See also
    --------
    k_components

    References
    ----------
    .. [1]  Torrents, J. and F. Ferraro (2015) Structural Cohesion: 
            Visualization and Heuristics for Fast Computation.
            http://arxiv.org/pdf/1503.04476v1

    .. [2]  White, Douglas R., and Mark Newman (2001) A Fast Algorithm for 
            Node-Independent Paths. Santa Fe Institute Working Paper #01-07-035
            http://eclectic.ss.uci.edu/~drwhite/working.pdf

    .. [3]  Moody, J. and D. White (2003). Social cohesion and embeddedness: 
            A hierarchical conception of social groups. 
            American Sociological Review 68(1), 103--28.
            http://www2.asanet.org/journals/ASRFeb03MoodyWhite.pdf

    """
    # Dictionary with connectivity level (k) as keys and a list of
    # sets of nodes that form a k-component as values
    k_components = collections.defaultdict(list)
    # make a few functions local for speed
    node_connectivity = local_node_connectivity
    k_core = nx.k_core
    core_number = nx.core_number
    biconnected_components = nx.biconnected_components
    density = nx.density
    combinations = itertools.combinations
    # Exact solution for k = {1,2}
    # There is a linear time algorithm for triconnectivity, if we had an
    # implementation available we could start from k = 4.
    for component in  nx.connected_components(G):
        # isolated nodes have connectivity 0
        comp = set(component)
        if len(comp) > 1:
            k_components[1].append(comp)
    for bicomponent in  nx.biconnected_components(G):
        # avoid considering dyads as bicomponents
        bicomp = set(bicomponent)
        if len(bicomp) > 2:
            k_components[2].append(bicomp)
    # There is no k-component of k > maximum core number
    # \kappa(G) <= \lambda(G) <= \delta(G)
    g_cnumber = core_number(G)
    max_core = max(g_cnumber.values())
    for k in range(3, max_core + 1):
        C = k_core(G, k, core_number=g_cnumber)
        for nodes in biconnected_components(C):
            # Build a subgraph SG induced by the nodes that are part of
            # each biconnected component of the k-core subgraph C.
            if len(nodes) < k:
                continue
            SG = G.subgraph(nodes)
            # Build auxiliary graph
            H = _AntiGraph()
            H.add_nodes_from(SG.nodes_iter())
            for u,v in combinations(SG, 2):
                K = node_connectivity(SG, u, v, cutoff=k)
                if k > K:
                    H.add_edge(u,v)
            for h_nodes in biconnected_components(H):
                if len(h_nodes) <= k:
                    continue
                SH = H.subgraph(h_nodes)
                for Gc in _cliques_heuristic(SG, SH, k, min_density):
                    for k_nodes in biconnected_components(Gc):
                        Gk = nx.k_core(SG.subgraph(k_nodes), k)
                        if len(Gk) <= k:
                            continue
                        k_components[k].append(set(Gk))
    return k_components


def _cliques_heuristic(G, H, k, min_density):
    h_cnumber = nx.core_number(H)
    for i, c_value in enumerate(sorted(set(h_cnumber.values()), reverse=True)):
        cands = set(n for n, c in h_cnumber.items() if c == c_value)
        # Skip checking for overlap for the highest core value
        if i == 0:
            overlap = False
        else:
            overlap = set.intersection(*[
                        set(x for x in H[n] if x not in cands)
                        for n in cands])
        if overlap and len(overlap) < k:
            SH = H.subgraph(cands | overlap)
        else:
            SH = H.subgraph(cands)
        sh_cnumber = nx.core_number(SH)
        SG = nx.k_core(G.subgraph(SH), k)
        while not (_same(sh_cnumber) and nx.density(SH) >= min_density):
            SH = H.subgraph(SG)
            if len(SH) <= k:
                break
            sh_cnumber = nx.core_number(SH)
            sh_deg = SH.degree()
            min_deg = min(sh_deg.values())
            SH.remove_nodes_from(n for n, d in sh_deg.items() if d == min_deg)
            SG = nx.k_core(G.subgraph(SH), k)
        else:
            yield SG


def _same(measure, tol=0):
    vals = set(measure.values())
    if (max(vals) - min(vals)) <= tol:
        return True
    return False


class _AntiGraph(nx.Graph):
    """
    Class for complement graphs.

    The main goal is to be able to work with big and dense graphs with
    a low memory foodprint.

    In this class you add the edges that *do not exist* in the dense graph,
    the report methods of the class return the neighbors, the edges and 
    the degree as if it was the dense graph. Thus it's possible to use
    an instance of this class with some of NetworkX functions. In this
    case we only use k-core, connected_components, and biconnected_components.
    """

    all_edge_dict = {'weight': 1}
    def single_edge_dict(self):
        return self.all_edge_dict
    edge_attr_dict_factory = single_edge_dict

    def __getitem__(self, n):
        """Return a dict of neighbors of node n in the dense graph.

        Parameters
        ----------
        n : node
           A node in the graph.

        Returns
        -------
        adj_dict : dictionary
           The adjacency dictionary for nodes connected to n.

        """
        all_edge_dict = self.all_edge_dict
        return dict((node, all_edge_dict) for node in 
                    set(self.adj) - set(self.adj[n]) - set([n]))

    def neighbors(self, n):
        """Return a list of the nodes connected to the node n in 
           the dense graph.

        Parameters
        ----------
        n : node
           A node in the graph

        Returns
        -------
        nlist : list
            A list of nodes that are adjacent to n.

        Raises
        ------
        NetworkXError
            If the node n is not in the graph.

        """
        try:
            return list(set(self.adj) - set(self.adj[n]) - set([n]))
        except KeyError:
            raise NetworkXError("The node %s is not in the graph."%(n,))

    def neighbors_iter(self, n):
        """Return an iterator over all neighbors of node n in the 
           dense graph.

        """
        try:
            return iter(set(self.adj) - set(self.adj[n]) - set([n]))
        except KeyError:
            raise NetworkXError("The node %s is not in the graph."%(n,))

    def degree(self, nbunch=None, weight=None):
        """Return the degree of a node or nodes in the dense graph.
        """
        if nbunch in self:      # return a single node
            return next(self.degree_iter(nbunch,weight))[1]
        else:           # return a dict
            return dict(self.degree_iter(nbunch,weight))

    def degree_iter(self, nbunch=None, weight=None):
        """Return an iterator for (node, degree) in the dense graph.

        The node degree is the number of edges adjacent to the node.

        Parameters
        ----------
        nbunch : iterable container, optional (default=all nodes)
            A container of nodes.  The container will be iterated
            through once.

        weight : string or None, optional (default=None)
           The edge attribute that holds the numerical value used 
           as a weight.  If None, then each edge has weight 1.
           The degree is the sum of the edge weights adjacent to the node.

        Returns
        -------
        nd_iter : an iterator
            The iterator returns two-tuples of (node, degree).

        See Also
        --------
        degree

        Examples
        --------
        >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
        >>> G.add_path([0,1,2,3])
        >>> list(G.degree_iter(0)) # node 0 with degree 1
        [(0, 1)]
        >>> list(G.degree_iter([0,1]))
        [(0, 1), (1, 2)]

        """
        if nbunch is None:
            nodes_nbrs = ((n, {v: self.all_edge_dict for v in
                            set(self.adj) - set(self.adj[n]) - set([n])})
                            for n in self.nodes_iter())
        else:
            nodes_nbrs = ((n, {v: self.all_edge_dict for v in
                            set(self.nodes()) - set(self.adj[n]) - set([n])})
                            for n in self.nbunch_iter(nbunch))

        if weight is None:
            for n,nbrs in nodes_nbrs:
                yield (n,len(nbrs)+(n in nbrs)) # return tuple (n,degree)
        else:
            # AntiGraph is a ThinGraph so all edges have weight 1
            for n,nbrs in nodes_nbrs:
                yield (n, sum((nbrs[nbr].get(weight, 1) for nbr in nbrs)) +
                              (n in nbrs and nbrs[n].get(weight, 1)))

    def adjacency_iter(self):
        """Return an iterator of (node, adjacency set) tuples for all nodes
           in the dense graph.

        This is the fastest way to look at every edge.
        For directed graphs, only outgoing adjacencies are included.

        Returns
        -------
        adj_iter : iterator
           An iterator of (node, adjacency set) for all nodes in
           the graph.

        """
        for n in self.adj:
            yield (n, set(self.adj) - set(self.adj[n]) - set([n]))
