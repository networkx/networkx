"""
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
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import networkx
from networkx.utils import is_string_like,_get_fh

def write_pajek(G, path):
    """Write NetworkX graph in pajek format to path.
    """
    fh=_get_fh(path,mode='w')

    fh.write("*network %s\n"%G.name)

    # write nodes with attributes
    fh.write("*vertices %s\n"%(G.order()))
    nodes = G.nodes()
    # make dictionary mapping nodes to integers
    nodenumber=dict(zip(nodes,range(1,len(nodes)+1))) 
    try:
        node_attr=G.node_attr
    except:
        node_attr={}
    for n in nodes:
        na=node_attr.get(n,{})
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
    for e in G.edges():
        if len(e)==3:
            u,v,d=e
            if type(d)!=type({}):
                if d is None:
                    d=1.0
                d={'value':float(d)}
        else:
            u,v=e
            d={}
        value=d.pop('value',1.0) # use 1 as default edge value
        fh.write("%d %d %f "%(nodenumber[u],nodenumber[v],float(value)))
        for k,v in d.items():
            if " " in v: # add quotes to any values with a blank space
                v="\"%s\""%v
            fh.write("%s %s "%(k,v))
        fh.write("\n")                               
    fh.close()

def read_pajek(path):
    """Read graph in pajek format from path. Returns an XGraph or XDiGraph.
    """
    fh=_get_fh(path,mode='r')        
    G=parse_pajek(fh)
    return G

def parse_pajek(lines):
    """Parse pajek format graph from string or iterable.."""
    import shlex
    if is_string_like(lines): lines=iter(lines.split('\n'))
    lines = iter([line.rstrip('\n') for line in lines])
    G=networkx.XDiGraph(selfloops=True) # are multiedges allowed in Pajek?
    G.node_attr={} # dictionary to hold node attributes
    directed=True # assume this is a directed network for now
    while lines:
        try:
            l=lines.next()
        except: #EOF
            break
        if l.startswith("*network"):
            label,name=l.split()
            G.name=name
        if l.startswith("*vertices"):
            nodelabels={}
            l,nnodes=l.split()
            for i in range(int(nnodes)):
                splitline=shlex.split(lines.next())
                id,label,x,y,shape=splitline[0:5]
                G.add_node(label)
                nodelabels[id]=label
                G.node_attr[label]={'id':id,'x':x,'y':y,'shape':shape}
                extra_attr=zip(splitline[5::2],splitline[6::2])
                G.node_attr[label].update(extra_attr)
        if l.startswith("*edges") or l.startswith("*arcs"):
            if l.startswith("*edge"):
                G=networkx.XGraph(G) # switch from digraph to graph
            for l in lines:
                splitline=shlex.split(l)
                ui,vi,w=splitline[0:3]
                u=nodelabels.get(ui,ui)
                v=nodelabels.get(vi,vi)
                edge_data={'value':float(w)}
                extra_attr=zip(splitline[3::2],splitline[4::2])
                edge_data.update(extra_attr)
                G.add_edge(u,v,edge_data)
    return G

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/readwrite/pajek.txt',package='networkx')
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
