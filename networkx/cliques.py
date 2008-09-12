"""
Cliques   - Find and manipulate cliques of graphs

Note that finding the largest clique of a graph has been
shown to be an NP complete problem so the algorithms here
could take a LONG time to run.  In practice it hasn't been 
too bad for the graphs tested.
"""
__author__ = """Dan Schult (dschult@colgate.edu)"""
__date__ = "$Date: 2005-06-15 07:56:03 -0600 (Wed, 15 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1021 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import networkx

def find_cliques(G):
    """
    Find_cliques algorithm based on Bron & Kerbosch
    
    This algorithm searchs for maximal cliques in a graph.
    maximal cliques are the largest complete subgraph containing
    a given point.  The largest maximal clique is sometimes called
    the maximum clique.
    
    This algorithm produces the list of maximal cliques each
    of which are a list of the members of the clique.
   
    Based on Algol algorithm published by Bron & Kerbosch
    A C version is available as part of the rambin package.
    http://www.ram.org/computing/rambin/rambin.html

    Reference::

        @article{362367,
        author = {Coen Bron and Joep Kerbosch},
        title = {Algorithm 457: finding all cliques of an undirected graph},
        journal = {Commun. ACM},
        volume = {16},
        number = {9},
        year = {1973},
        issn = {0001-0782},
        pages = {575--577},
        doi = {http://doi.acm.org/10.1145/362342.362367},
        publisher = {ACM Press},
        }
    """
    all_nodes=G.nodes()
    num_nodes=G.order()
    clique=[]
    cliques=[]
    _extend(all_nodes,0,num_nodes,G,clique,cliques)
    return cliques

def _extend(old_nodes,num_not,num_left,G,clique,cliques):
    """ 
    A recursive helper routine for find_cliques
 
    This recursive routine explores the "old_nodes" set of nodes
    for complete subgraphs.  num_left is the size of old_nodes. 
    The first num_not nodes are called the "not" group by B&K
    because they have already been considered. 
    The rest (num_left-num_not) of them are called "candidates".
 
    G is the graph, 
    clique is the clique being built,
    cliques is a list of maximal cliques found so far.
    """
    # set up sets nots and cands for easy reference
    cands=old_nodes[num_not:]
    nots=old_nodes[:num_not]
 
    #  Look for nodes that are "candidates" with the
    #  most neighbors among the "candidates"
    max_conn=0
    scands=set(cands)
    for p in cands:
        conn=len(scands & set(G[p]))
        if conn>max_conn:
            fixp=p
            max_conn=conn
            if max_conn > num_left-1: break  # found a most connected node
   
    # Note: if max_conn still zero, then no connections among candidates
    #     We can take a shortcut.
    #     If connects to a "not" node, we already got that clique
    #     Otherwise adding it makes a clique!
    if max_conn==0:
        for v in cands:
            not_conn=0
            isneighbor=lambda u:G.has_edge(v,u)  #"isneighbor" function
            for u in nots:
                if isneighbor(u):
                    not_conn=1
                    break
            if not_conn==0:
##              print "New Maximal Clique Found!",clique
                cliques.append( clique+[v] )
        return

    # Set up the Best Candidate as our fixed point for this tree
    # best_position=old_nodes.index(fixp)
    fixpneighbor=lambda v: G.has_edge(fixp,v) #"isneighbor" function
    v=fixp
 
    # Go through each of the candidate 
    # nodes trying to build a clique
    #       cntr counts how many are left to check
    for cntr in range(num_left-num_not-max_conn,0,-1):
        # add the best node to the list of clique
##      print tt,"next candidate is:",v
        clique.append(v)
        isneighbor=lambda u: G.has_edge(v,u) # "isneighbor" function

        # Now create new lists to send to next recursion
        # fill new array--starting with "not" nodes
        new=[ u for u in nots if isneighbor(u)]
        new_num_not=len(new)
        # now fill rest of new array with "candidate" nodes
        new.extend( [ u for u in cands if isneighbor(u)] )
        new_num_left=len(new)

        # check if zero or one node left
        if new_num_left == 0:
            # Now there are no nodes left in "cand" or "not" to look at
            # we have found a maximal clique!!!
            cliques.append(clique[:])
##          print tt,"No nodes left so it must be a clique!"
##          print tt,"New Maximal Clique Found!",clique
        elif new_num_not<new_num_left:
            if new_num_left==1:
                #  Only one node left so it must be a clique!
##              print tt,"Only one node left so it must be a clique!"
##              print tt,"New Maximal Clique Found!",clique
                cliques.append(clique+new)
            else:
                # Recursion on this routine
##              print tt,"Going into extend with cntr=",cntr
##              tt=tt + "  "
                _extend(new,new_num_not,new_num_left,G,clique,cliques)
##              tt=tt[0:len(tt)-2]  # go back to previous indentation 

        # Done with checking branches for this node,
        # remove it from clique and add it to the NOT group
        clique.remove(v)
        nots.append(v)
        cands.remove(v)
        # find next candidate
        pos=0
        if cntr>1:
            while fixpneighbor(cands[pos]):
                pos += 1
            v=cands[pos]

def make_max_clique_graph(G,create_using=None,name=None):
    """ 
    Create the maximal clique graph of a graph.
    It finds the maximal cliques and treats these as nodes.
    The nodes are connected if they have common members in 
    the original graph.  Theory has done a lot with clique
    graphs, but I haven't seen much on maximal clique graphs.

    Note: This should be the same as make_clique_bipartite followed
    by project_up, but it saves all the intermediate stuff.
    """
    cliq=find_cliques(G)
    size=len(cliq)
    if create_using:
        B=create_using
        B.clear()
    else:
        B=networkx.Graph()
    if name is not None:
        B.name=name

    for i in range(1,size+1):
        B.add_node(i)
        cl=cliq[i-1]
        for j in range(i+1,size+1):
            other_cl=cliq[j-1]
            intersect=[ w for w in cl if w in other_cl ]
            if intersect:     # Not empty list
                B.add_edge(i,j)
    return B

def make_clique_bipartite(G,fpos=None,create_using=None,name=None):
    """ 
    Create a bipartite clique graph from a graph G.
    Nodes of G are retained as the "bottom nodes" of B and 
    cliques of G become "top nodes" of B.
    Edges are present if a bottom node belongs to the clique 
    represented by the top node.
 
    Returns a Graph with additional attribute B.node_type
    which is "Bottom" or "Top" appropriately.

    if fpos is not None, a second additional attribute B.pos
    is created to hold the position tuple of each node for viewing
    the bipartite graph.
    """
    cliq=find_cliques(G)
    if create_using:
        B=create_using
        B.clear()
    else:
        B=networkx.Graph()
    if name is not None:
        B.name=name

    B.add_nodes_from(G)
    B.node_type={}   # New Attribute for B
    for n in B:
        B.node_type[n]="Bottom"
 
    i=0
    if fpos is not None: 
        B.pos={}     # New Attribute for B
        delta_cpos=1./len(cliq)
        delta_ppos=1./G.order()
        cpos=0.
        ppos=0.
    for cl in cliq:
        i += 1
        name= -i   # Top nodes get negative names
        B.add_node(name)
        B.node_type[name]="Top"
        if fpos is not None: 
            if not B.pos.has_key(name):
                B.pos[name]=(0.2,cpos)
                cpos +=delta_cpos
        for v in cl:
            B.add_edge(name,v)
            if fpos is not None:
                if not B.pos.has_key(v):
                    B.pos[v]=(0.8,ppos)
                    ppos +=delta_ppos
    return B
   
def project_down(B,create_using=None,name=None):
    """ 
    Project a bipartite graph B down onto its "Bottom Nodes".
    The nodes retain their names and are connected if they
    share a common Top Node in the Bipartite Graph.
    Returns a Graph.
    """
    if create_using:
        G=create_using
        G.clear()
    else:
        G=networkx.Graph()
    if name is not None:
        G.name=name

    for v in B.nodes():
        if B.node_type[v]=="Bottom":
            G.add_node(v)
            for cv in B.neighbors(v):
                G.add_edges_from([(v,u) for u in B.neighbors(cv)])
    return G
 
def project_up(B,create_using=None,name=None):
    """ 
    Project a bipartite graph B up onto its "Top Nodes".
    The nodes retain their names and are connected if they
    share a common Bottom Node in the Bipartite Graph.
    Returns a Graph.
    """
    if create_using:
        G=create_using
        G.clear()
    else:
        G=networkx.Graph()
    if name is not None:
        G.name=name

    for v in B.nodes():
        if B.node_type[v]=="Top":
            vname= -v   #Change sign of name for Top Nodes
            G.add_node(vname)
            for cv in B.neighbors(v):
                # Note: -u changes the name (not Top node anymore)
                G.add_edges_from([(vname,-u) for u in B.neighbors(cv) if u!=v])
    return G
 
def graph_clique_number(G,cliques=None):
    """Return the clique number (size the largest clique) for G.
       Optional list of cliques can be input if already computed.
    """
    if cliques is None:
        cliques=find_cliques(G)
    return   max( [len(c) for c in cliques] )


def graph_number_of_cliques(G,cliques=None):
    """  Returns the number of maximal cliques in G
       Optional list of cliques can be input if already computed.
    """
    if cliques is None:
        cliques=find_cliques(G)
    return   len(cliques)

 
def node_clique_number(G,nodes=None,with_labels=False,cliques=None):
    """ Returns the size of the largest maximal clique containing
        each given node.  

        Returns a single or list depending on input nodes.
        Returns a dict keyed by node if "with_labels=True".
        Optional list of cliques can be input if already computed.
    """
    if nodes is None:                 # none, use entire graph
        nodes=G.nodes()
    elif  not isinstance(nodes, list):    # check for a list
        nodes=[nodes]             # assume it is a single value

    if cliques is None:
        cliques=find_cliques(G)
    d={}
    for v in nodes:
        d[v]=max([len(c) for c in cliques if v in c])
    
    if with_labels: return d
    if len(d)==1: return d[v] #return single value
    return d.values()


def number_of_cliques(G,nodes=None,cliques=None,with_labels=False):
    """ Returns the number of maximal cliques for each node.

        Returns a single or list depending on input nodes.
        Returns a dict keyed by node if "with_labels=True".
        Optional list of cliques can be input if already computed.
    """
    if nodes is None:
        nodes=G.nodes()   # none, get entire graph
    elif  not isinstance(nodes, list):    # check for a list
        nodes=[nodes]             # assume it is a single value

    if cliques is None:
        cliques=find_cliques(G)
    numcliq={}
    for v in nodes:
        numcliq[v]=len([1 for c in cliques if v in c])

    if with_labels: return numcliq
    if len(numcliq)==1: return numcliq[v]
    return numcliq.values()
    
def cliques_containing_node(G,nodes=None,cliques=None,with_labels=False):
    """ Returns a list of cliques containing the given node.

        Returns a single list or list of lists depending on input nodes.
        Returns a dict keyed by node if "with_labels=True".
        Optional list of cliques can be input if already computed.
    """
    if nodes is None:
        nodes=G.nodes()   # none, get entire graph
    elif  not isinstance(nodes, list):    # check for a list
        nodes=[nodes]             # assume it is a single value

    if cliques is None:
        cliques=find_cliques(G)
    vcliques={}
    for v in nodes:
        vcliques[v]=[c for c in cliques if v in c]

    if with_labels: return vcliques
    if len(vcliques)==1: return vcliques[v]
    return vcliques.values()

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/cliques.txt',package='networkx')
    return suite


if __name__ == "__main__":
    import os   
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
    
