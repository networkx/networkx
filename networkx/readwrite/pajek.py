"""
*****
Pajek
*****
Read graphs in Pajek format.

This implementation handles directed and undirected graphs including
those with self loops and parallel edges.  

Format
------

See http://vlado.fmf.uni-lj.si/pub/networks/pajek/doc/draweps.htm
for format information.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2008-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
from networkx.utils import is_string_like,get_file_handle,make_str

__all__ = ['read_pajek', 'parse_pajek', 'generate_pajek', 'write_pajek']

def safe_string(s):
    """add quotes to any values with a blank space"""
    if " " in s:
        return "\"%s\""%s
    return s

def generate_pajek(G):
    """Generate lines in Pajek graph format.

    Parameters
    ----------
    G : graph
       A Networkx graph

    References
    ----------
    See http://vlado.fmf.uni-lj.si/pub/networks/pajek/doc/draweps.htm
    for format information.
    """
    if G.name=='': 
        name='NetworkX'
    else:
        name=G.name
    yield '*network %s'%name

    # write nodes with attributes
    yield '*vertices %s'%(G.order())
    nodes = G.nodes()
    # make dictionary mapping nodes to integers
    nodenumber=dict(zip(nodes,range(1,len(nodes)+1))) 
    for n in nodes:
        na=G.node.get(n,{})
        x=na.get('x',0.0)
        y=na.get('y',0.0)
        id=int(na.get('id',nodenumber[n]))
        nodenumber[n]=id
        shape=na.get('shape','ellipse')
        s=' '.join(map(make_str,(id,safe_string(n),x,y,shape)))
        for k,v in na.items():
            if is_string_like(v):
                v=safe_string(v)
            s+=' %s %s'%(k,v)
        yield s

    # write edges with attributes         
    if G.is_directed():
        yield '*arcs'
    else:
        yield '*edges'
    for u,v,edgedata in G.edges(data=True):
        d=edgedata.copy()
        value=d.pop('weight',1.0) # use 1 as default edge value
        s=' '.join(map(make_str,(nodenumber[u],nodenumber[v],value)))
        for k,v in d.items():
            if is_string_like(v):
                v=safe_string(v)
            s+=' %s %s'%(k,v)
        yield s
        
def write_pajek(G, path, encoding='UTF-8'):
    """Write graph in Pajek format to path.

    Parameters
    ----------
    G : graph
       A Networkx graph
    path : file or string
       File or filename to write.  
       Filenames ending in .gz or .bz2 will be compressed.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_pajek(G, "test.net")

    References
    ----------
    See http://vlado.fmf.uni-lj.si/pub/networks/pajek/doc/draweps.htm
    for format information.
    """
    fh=get_file_handle(path, 'wb')
    for line in generate_pajek(G):
        line+='\n'
        fh.write(line.encode(encoding))

def read_pajek(path,encoding='UTF-8'):
    """Read graph in Pajek format from path. 

    Parameters
    ----------
    path : file or string
       File or filename to write.  
       Filenames ending in .gz or .bz2 will be uncompressed.

    Returns
    -------
    G : NetworkX MultiGraph or MultiDiGraph.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> nx.write_pajek(G, "test.net")
    >>> G=nx.read_pajek("test.net")

    To create a Graph instead of a MultiGraph use

    >>> G1=nx.Graph(G)

    References
    ----------
    See http://vlado.fmf.uni-lj.si/pub/networks/pajek/doc/draweps.htm
    for format information.
    """
    fh=get_file_handle(path, 'rb')
    lines = (line.decode(encoding) for line in fh)
    return parse_pajek(lines)

def parse_pajek(lines):
    """Parse Pajek format graph from string or iterable.

    Parameters
    ----------
    lines : string or iterable
       Data in Pajek format.

    Returns
    -------
    G : NetworkX graph

    See Also
    --------
    read_pajek()

    """
    import shlex
    # multigraph=False
    if is_string_like(lines): lines=iter(lines.split('\n'))
    lines = iter([line.rstrip('\n') for line in lines])
    G=nx.MultiDiGraph() # are multiedges allowed in Pajek? assume yes
    while lines:
        try:
            l=next(lines)
        except: #EOF
            break
        if l.lower().startswith("*network"):
            label,name=l.split()
            G.name=name
        if l.lower().startswith("*vertices"):
            nodelabels={}
            l,nnodes=l.split()
            for i in range(int(nnodes)):
                splitline=shlex.split(str(next(lines)))
                id,label=splitline[0:2]
                G.add_node(label)
                nodelabels[id]=label
                G.node[label]={'id':id}
                try: 
                    x,y,shape=splitline[2:5]
                    G.node[label].update({'x':float(x),
                                          'y':float(y),
                                          'shape':shape})
                except:
                    pass
                extra_attr=zip(splitline[5::2],splitline[6::2])
                G.node[label].update(extra_attr)
        if l.lower().startswith("*edges") or l.lower().startswith("*arcs"):
            if l.lower().startswith("*edge"):
               # switch from multidigraph to multigraph
                G=nx.MultiGraph(G)
            if l.lower().startswith("*arcs"):
               # switch to directed with multiple arcs for each existing edge
                G=G.to_directed()
            for l in lines:
                splitline=shlex.split(str(l))
                if len(splitline)<2:
                    continue
                ui,vi=splitline[0:2]
                u=nodelabels.get(ui,ui)
                v=nodelabels.get(vi,vi)
                # parse the data attached to this edge and put in a dictionary 
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
                # if G.has_edge(u,v):
                #     multigraph=True
                G.add_edge(u,v,**edge_data)
    return G


# fixture for nose tests
def teardown_module(module):
    import os
    os.unlink('test.net')
