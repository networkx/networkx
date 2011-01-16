# encoding: utf-8
"""
Functions for creating network blockmodels from node partitions.

Created by Drew Conway <drew.conway@nyu.edu> 
Copyright (c) 2010. All rights reserved.
"""
__author__ = """\n""".join(['Drew Conway <drew.conway@nyu.edu>',
                            'Aric Hagberg <hagberg@lanl.gov>'])
__all__=['blockmodel']

import networkx as nx

def blockmodel(G,partitions,multigraph=False):
    """Returns a reduced graph constructed using the generalized block modeling
    technique.

    The blockmodel technique collapses nodes into blocks based on a
    given partitioning of the node set.  Each partition of nodes
    (block) is represented as a single node in the reduced graph.

    Edges between nodes in the block graph are added according to the
    edges in the original graph.  If the parameter multigraph is False
    (the default) a single edge is added with a weight equal to the
    sum of the edge weights between nodes in the original graph
    The default is a weight of 1 if weights are not specified.  If the
    parameter multigraph is True then multiple edges are added each
    with the edge data from the original graph.

    Parameters
    ----------
    G : graph
        A networkx Graph or DiGraph
    partitions : list of lists, or list of sets 
        The partition of the nodes.  Must be non-overlapping.
    multigraph : bool, optional
        If True return a MultiGraph with the edge data of the original
        graph applied to each corresponding edge in the new graph.
        If False return a Graph with the sum of the edge weights, or a
        count of the edges if the original graph is unweighted.

    Returns
    -------
    blockmodel : a Networkx graph object
    
    Examples
    --------
    >>> G=nx.path_graph(6)
    >>> partition=[[0,1],[2,3],[4,5]]
    >>> M=nx.blockmodel(G,partition)

    References
    ----------
    .. [1] Patrick Doreian, Vladimir Batagelj, and Anuska Ferligoj
    	"Generalized Blockmodeling",Cambridge University Press, 2004.
    """
    # Create sets of node partitions
    part=list(map(set,partitions)) 

    # Check for overlapping node partitions
    u=set()
    for p1,p2 in zip(part[:-1],part[1:]):
        u.update(p1)
        #if not u.isdisjoint(p2):  # Python 2.6 required
        if len (u.intersection(p2))>0:
            raise nx.NetworkXException("Overlapping node partitions.")

    # Initialize blockmodel graph
    if multigraph:
        if G.is_directed():
            M=nx.MultiDiGraph() 
        else:
            M=nx.MultiGraph() 
    else:
        if G.is_directed():
            M=nx.DiGraph() 
        else:
            M=nx.Graph() 
        
    # Add nodes and properties to blockmodel            
    # The blockmodel nodes are node-induced subgraphs of G
    # Label them with integers starting at 0
    for i,p in zip(range(len(part)),part):
        M.add_node(i)
        # The node-induced subgraph is stored as the node 'graph' attribute 
        SG=G.subgraph(p)
        M.node[i]['graph']=SG        
        M.node[i]['nnodes']=SG.number_of_nodes()
        M.node[i]['nedges']=SG.number_of_edges()
        M.node[i]['density']=nx.density(SG)
        
    # Create mapping between original node labels and new blockmodel node labels
    block_mapping={}
    for n in M:
        nodes_in_block=M.node[n]['graph'].nodes()
        block_mapping.update(dict.fromkeys(nodes_in_block,n))

    # Add edges to block graph 
    for u,v,d in G.edges(data=True):
        bmu=block_mapping[u]
        bmv=block_mapping[v]
        if bmu==bmv: # no self loops
            continue
        if multigraph: 
            # For multigraphs add an edge for each edge in original graph
            M.add_edge(bmu,bmv,attr_dict=d)
        else:
            # For graphs and digraphs add single weighted edge
            weight=d.get('weight',1.0) # default to 1 if no weight specified
            if M.has_edge(bmu,bmv):
                M[bmu][bmv]['weight']+=weight
            else:
                M.add_edge(bmu,bmv,weight=weight)
    return M

