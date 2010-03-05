#!/usr/bin/env python
# encoding: utf-8
"""
Example of creating a block model using the blockmodel function in NX.  Data used is the Hartford, CT drug users network:

@article{,
	title = {Social Networks of Drug Users in {High-Risk} Sites: Finding the Connections},
	volume = {6},
	shorttitle = {Social Networks of Drug Users in {High-Risk} Sites},
	url = {http://dx.doi.org/10.1023/A:1015457400897},
	doi = {10.1023/A:1015457400897},
	number = {2},
	journal = {{AIDS} and Behavior},
	author = {Margaret R. Weeks and Scott Clair and Stephen P. Borgatti and Kim Radda and Jean J. Schensul},
	month = jun,
	year = {2002},
	pages = {193--206}
}

"""

__author__="""Drew Conway (drew.conway@nyu.edu)"""

import networkx as nx
from numpy import zeros
from scipy.cluster import hierarchy
from scipy.spatial import distance
import matplotlib.pyplot as plt

def create_hc(G):
    """Creates hierarchical cluster of graph G from distance matrix"""
    v=G.nodes()
    distances=zeros((len(v),len(v)))
    # Generate matrix of geodesic distance
    for n in v:
        for m in v:
            if n!=m:
                distances[n][m]=nx.shortest_path_length(G,m,n)
    # Create hierarchical cluster
    Y=distance.squareform(distances)
    Z=hierarchy.complete(Y)  # Creates HC using farthest point linkage
    membership=list(hierarchy.fcluster(Z,t=1.15)) #Partition selection is arbitrary, for illustrive purposes
    # Create collection of lists for blockmodel 
    partitions=[]
    for i in range(0,max(membership)):
        partitions.append([])
        for j in range(0,len(membership)):
            if membership[j]==i+1:
                partitions[i].append(j)
    return partitions

if __name__ == '__main__':
    try:
        G=nx.read_edgelist("hartford_drug.edgelist")
    except IOError:
        raise "hartford_drug.edgelist not found"
    
    # Extract largest connected component
    drug_main=nx.connected_component_subgraphs(G)[0]
    drug_main=nx.convert_node_labels_to_integers(drug_main) # Makes life easier
    partitions=create_hc(drug_main)
    bm=nx.blockmodel(drug_main,partitions)
    
    # Draw block model with weighted edges and nodes sized by internal density
    pos=nx.spring_layout(bm)
    ns=map(lambda x: bm.node[x]['nnodes']*10,bm.nodes())
    el=[(u,v) for (u,v,d) in bm.edges(data=True)]
    es=[(2*d['weight']) for (u,v,d) in bm.edges(data=True)]
    # Plot and save
    fig=plt.figure(1,figsize=(6,10))
    ax=fig.add_subplot(211)
    nx.draw(drug_main,with_labels=False,node_size=10)
    ax=fig.add_subplot(212)
    nx.draw_networkx_nodes(bm,pos,node_size=ns)
    nx.draw_networkx_edges(bm,pos,edgelist=el,width=es,alpha=1.0)
    plt.axis('off')
    plt.savefig('drug_block_model.png')
    
    
    
