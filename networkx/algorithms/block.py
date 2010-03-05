# encoding: utf-8
"""
Functions for creating network blockmodels from node partitions.

Created by Drew Conway <drew.conway@nyu.edu> 
Copyright (c) 2010. All rights reserved.
"""
__author__ = """\n""".join(['Drew Conway <drew.conway@nyu.edu>',
                            'Aric Hagberg <hagberg@lanl.gov>'])
__all__=['blockmodel']

import networkx

def blockmodel(G,partitions,multigraph=False):
    """Generates a new graph using the generalized block modeling technique.

    The technique collapses nodes into blocks based on a given partitioning
    of the node set.  Each partition of nodes (block) is represented
    as a single node in the reduced graph.  

    Edges between nodes in the block graph are added according to
    the edges in the original graph.  If the parameter multigraph is False
    (the default) a single edge is added with a weight equal to
    the sum of the edge weights between nodes in the original graph
    (default of weight=1 if not weights are specified).  If the
    parameter multigraph is True then multiple edges are added between
    the block nodes each with the edge data from the original graph.

    Parameters
    ----------
    G : graph
        A networkx Graph or DiGraph
    partitions : list of lists or list of sets
        The partition of the nodes.  Must be non-overlapping.
    multigraph: bool (optional)
        If True return a MultiGraph with the edge data of the original
        graph applied to each corresponding edge in the new graph.
        If False return a Graph with the sum of the edge weights or a
        count of the edges if the original graph is unweighted.

    Returns
    -------
    blockmodel : a Networkx graph object
    
    Examples
    --------
    >>> G=networkx.path_graph(6)
    >>> partition=[[0,1],[2,3],[4,5]]
    >>> M=blockmodel(G,partition)

    Notes
    -----
    For reference see:
    @book{doreian_generalized_2004,
    	title = {Generalized Blockmodeling},
    	isbn = {0521840856},
    	publisher = {Cambridge University Press},
    	author = {Patrick Doreian and Vladimir Batagelj and Anuska Ferligoj},
    	month = nov,
    	year = {2004}
    }
    """
    part=map(set,partitions) # create sets of node partitions
    u=set()
    for p1,p2 in zip(part[:-1],part[1:]):
        u.update(p1)
        if not u.isdisjoint(p2):
            raise networkx.NetworkXException("Overlapping node partitions.")

    if multigraph:
        if G.is_directed():
            M=networkx.MultiDiGraph() 
        else:
            M=networkx.MultiGraph() 
    else:
        if G.is_directed():
            M=networkx.DiGraph() 
        else:
            M=networkx.Graph() 
        

    # Nodes in new graph are are node-induced subgraphs of G
    # Label them with integers starting at 0
    for i,p in zip(range(len(part)),part):
        M.add_node(i)
        # the node-induced subgraph is stored as the 'graph' attribute 
        SG=G.subgraph(p)
        M.node[i]['graph']=SG        
        M.node[i]['nnodes']=SG.number_of_nodes()
        M.node[i]['nedges']=SG.number_of_edges()
        M.node[i]['density']=networkx.density(SG)
        
    # Make mapping between original nodes and new block nodes
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
            M.add_edge(bmu,bmv,attr_dict=d)
        else:
            weight=d.get('weight',1.0) # default to 1 if no weight specified
            if M.has_edge(bmu,bmv):
                M[bmu][bmv]['weight']+=weight
            else:
                M.add_edge(bmu,bmv,weight=weight)
    return M


if __name__=='__main__':
    import networkx
    G=networkx.path_graph(6)
#    G=networkx.complete_graph(6)
    partition=[[0,1],[2,3],[4,5]]
    M=blockmodel(G,partition,multigraph=True)
    
