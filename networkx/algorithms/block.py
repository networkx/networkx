# encoding: utf-8
"""
Functions for creating network blockmodels from node partitions

Created by Drew Conway <drew.conway@nyu.edu> 
Copyright (c) 2010. All rights reserved.
"""
__author__ = """\n""".join(['Drew Conway <drew.conway@nyu.edu>',
                            'Aric Hagberg <hagberg@lanl.gov>'])
__all__=['blockmodel']

import networkx

def blockmodel(G,partitions,multigraph=False):
    """Generates a new graph using the generalized block modeling technique.

    The technique collpases nodes into blocks based on a given partitioning
    of the node set.  Each partition of nodes (block) is a single node in
    the new graph consiting of a Graph containing the node-induced
    subgraph.  

    Edges between nodes in the block graph are added for each edge
    between nodes in the corresponding partition.

    Parameters
    ----------
    G : graph
        A networkx Graph or DiGraph
    partitions : list of containers
        The partition of the nodes.  Must be non-overlapping.
    multigraph: bool (optional)
        If True return a MultiGraph with original edge data, if False
        return a Graph with the sum of the edge weights or count
        of the edges if the original graph is unweighted.

    Returns
    -------
    blockmodel : a Networkx graph object
    
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
        # the node-induced sugraph is an stored as the 'graph' attribute 
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
            M.add_edge(bmu,bmv,data=d)
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
    M=blockmodel(G,partition)
    
