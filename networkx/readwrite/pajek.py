"""
*****
Pajek
*****

Read graphs in Pajek format.

See http://vlado.fmf.uni-lj.si/pub/networks/pajek/doc/draweps.htm
for format information.

This implementation handles only directed and undirected graphs including
those with self loops and parallel edges.  

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
from networkx.utils import is_string_like,_get_fh

__all__ = ['read_pajek', 'parse_pajek', 'write_pajek']

def write_pajek(G, path):
    """Write in Pajek format to path.

    Parameters
    ----------
    G : graph
       A networkx graph
    path : file or string
       File or filename to write.  
       Filenames ending in .gz or .bz2 will be compressed.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_pajek(G, "test.net")
    """
    fh=_get_fh(path,mode='w')

    if G.name=='': 
        name="NetworkX"
    else:
        name=G.name
    fh.write("*network %s\n"%name)

    # write nodes with attributes
    fh.write("*vertices %s\n"%(G.order()))
    nodes = G.nodes()
    # make dictionary mapping nodes to integers
    nodenumber=dict(zip(nodes,range(1,len(nodes)+1))) 
    for n in nodes:
        na=G.node[n].copy()
        x=na.pop('x',0.0)
        y=na.pop('y',0.0)
        id=int(na.pop('id',nodenumber[n]))
        nodenumber[n]=id
        shape=na.pop('shape','ellipse')
        fh.write("%d \"%s\" %f %f %s "%(id,n,float(x),float(y),shape))
        for k,v in na.items():
            fh.write("%s %s "%(k,v))
        fh.write("\n")                               
        
    # write edges with attributes         
    if G.is_directed():
        fh.write("*arcs\n")
    else:
        fh.write("*edges\n")
    for u,v,edgedata in G.edges(data=True):
        d=edgedata.copy()
        value=d.pop('weight',1.0) # use 1 as default edge value
        fh.write("%d %d %f "%(nodenumber[u],nodenumber[v],float(value)))
        for k,v in d.items():
            if is_string_like(v):
                # add quotes to any values with a blank space
                if " " in v: 
                    v="\"%s\""%v
            fh.write("%s %s "%(k,v))
        fh.write("\n")                               
#    fh.close()

def read_pajek(path):
    """Read graph in Pajek format from path. 

    Returns a MultiGraph or MultiDiGraph.

    Parameters
    ----------
    path : file or string
       File or filename to write.  
       Filenames ending in .gz or .bz2 will be compressed.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_pajek(G, "test.net")
    >>> G=nx.read_pajek("test.net")

    To create a Graph instead of a MultiGraph use

    >>> G1=nx.Graph(G)


    """
    fh=_get_fh(path,mode='r')        
    G=parse_pajek(fh)
    return G

def parse_pajek(lines,edge_attr=True):
    """Parse pajek format graph from string or iterable.

    Primarily used as a helper for read_pajek().

    See Also
    --------
    read_pajek()

    """
    import shlex
    if is_string_like(lines): lines=iter(lines.split('\n'))
    lines = iter([line.rstrip('\n') for line in lines])
    G=nx.MultiDiGraph() # are multiedges allowed in Pajek?
    directed=True # assume this is a directed network for now
    while lines:
        try:
            l=lines.next()
        except: #EOF
            break
        if l.lower().startswith("*network"):
            label,name=l.split()
            G.name=name
        if l.lower().startswith("*vertices"):
            nodelabels={}
            l,nnodes=l.split()
            for i in range(int(nnodes)):
                splitline=shlex.split(lines.next())
                id,label=splitline[0:2]
                G.add_node(label)
                nodelabels[id]=label
                G.node[label]={'id':id}
                try: 
                    x,y,shape=splitline[2:5]
                    G.node[label].update({'x':x,'y':y,'shape':shape})
                except:
                    pass
                extra_attr=zip(splitline[5::2],splitline[6::2])
                G.node[label].update(extra_attr)
        if l.lower().startswith("*edges") or l.lower().startswith("*arcs"):
            if l.lower().startswith("*edge"):
               # switch from digraph to graph
                G=nx.MultiGraph(G)
            for l in lines:
                splitline=shlex.split(l)
                ui,vi=splitline[0:2]
                u=nodelabels.get(ui,ui)
                v=nodelabels.get(vi,vi)
                # parse the data attached to this edge and
                # put it in a dictionary 
                edge_data={}
                try:
                    # there should always be a single value on the edge?
                    w=splitline[2:3]
                    edge_data.update({'weight':float(w[0])})
                except:
                    pass
                    # if there isn't, just assign a 1
#                    edge_data.update({'value':1})
                extra_attr=zip(splitline[3::2],splitline[4::2])
                edge_data.update(extra_attr)
                G.add_edge(u,v,**edge_data)

    return G

