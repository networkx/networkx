# encoding: utf-8
"""Algorithms regarding cographs."""
import networkx as nx
__author__ = """\n""".join(['Jonas Nyrup <jnyrup@gmail.com>'])
__all__ = ['modularDecomposition', 'isCograph']


def modularDecomposition(G):
    """ Computes the cotree of a cograph.
    This is done by modular decomposition - http://en.wikipedia.org/wiki/Modular_decomposition
    As the algorithm only works for initial connected graphs, for non-connected graphs the algorithm is applied to the complement graph.

    Parameters
    ----------
    G : graph
        A networkx graph
        As cotrees can only be computed for cographs an error is raised if the input graph is not a cograph

    Returns
    -------
    out : graph
        The resulting cotree
    """
    if hasattr(G, 'graph') and isinstance(G.graph, dict):
        Gres = nx.DiGraph()
        if nx.is_connected(G):
            decomp(G, Gres, 1)
        else:
            # The cotree T' of G', is exactly T with 0 and 1 nodes interchanged.
            # http://www.lirmm.fr/~paul/Biblio/Postscript/wg03.pdf Section 1.2 observation 2
            decomp(nx.complement(G), Gres, 0)
        return Gres
    else:
        raise nx.NetworkXError("Input is not a correct NetworkX graph.")


def decomp(G, Gres, rootLabel):
    # list of modules from complement graph
    modules = nx.connected_component_subgraphs(nx.complement(G))
    if len(modules) == 1:
        if len(modules[0]) == 1:
            # return leaf node
            return modules[0].nodes()[0]
        else:
            raise nx.NetworkXUnfeasible(
                "input graph is not a valid cograph and corresponding cotree cannot be computed")
    else:
        # add internal node and connect all trees above as children
        root = nx.utils.generate_unique_node()
        Gres.add_node(root, label=rootLabel)
        Gres.add_edges_from([(root, decomp(module, Gres, 1 - rootLabel)) for module in modules])
        # return new internal root node
        return root


def isCograph(G):
    """ Determines whether G is a valid cograph
    Parameters
    ----------
    G : graph
        A networkx graph

    Returns
    -------
    out : bool
        Boolean stating whether input graph is a valid cograph
    """
    if hasattr(G, 'graph') and isinstance(G.graph, dict):
        if len(G) <= 3:
            # every graph of at most size 3 are cographs
            return True
        if nx.is_connected(G):
            return isCographAux(G)
        else:
            return isCographAux(nx.complement(G))
    else:
        raise nx.NetworkXError("Input is not a correct NetworkX graph.")


def isCographAux(G):
    modules = nx.connected_component_subgraphs(nx.complement(G))
    if len(modules) == 1:
        if len(modules[0]) == 1:
            # return leaf node
            return True
        else:
            return False
    else:
        return all(isCographAux(module) for module in modules)
