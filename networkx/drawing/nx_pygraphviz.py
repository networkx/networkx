"""
Import and export networkx networks to dot format using pygraphviz.

Provides:

 - write_dot()
 - read_dot()
 - graphviz_layout()
 - pygraphviz_layout()

 - pygraphviz_from_networkx()
 - networkx_from_pygraphviz()

and the graph layout methods:

 - graphviz_layout()
 - pygraphviz_layout()
 
Either this module or nx_pydot can be used to interface with graphviz.  

References:
 - pygraphviz    : http://networkx.lanl.gov/pygraphviz/
 - Graphviz:	   http://www.research.att.com/sw/tools/graphviz/
 - DOT Language:   http://www.research.att.com/~erg/graphviz/info/lang.html

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-06-15 08:55:33 -0600 (Wed, 15 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1034 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import os
import sys
from networkx.utils import is_string_like
try:
    import pygraphviz
except ImportError:
    raise


def write_dot(G,path=False):
    """Write G to a graphviz dot file."""
    A=pygraphviz_from_networkx(G)
    if path:
        try: 
            fh=open(path,'w')
        except IOError:                     
            print "Can't write"%path
            raise
        A.write(fh)
    else:
        print A.write(sys.stdout) # write on stdout
    return

def read_dot(path=False):
    """Creates an networkx graph from a dot file"""

    if path:
        try: 
            fh=open(path,'r')
        except IOError:                     
            print "The file %s does not exist"%path
            raise
    else:
        fh=sys.stdin  # no path, read from stdin
    A=pygraphviz.Agraph()
    A.read(fh)
    return networkx_from_pygraphviz(A)


def pygraphviz_from_networkx(N,
                             graph_attr=None,
                             node_attr=None,
                             edge_attr=None):
	"""Creates a pygraphviz graph from an networkx graph N"""

        if graph_attr is None:
            graph_attr={}
        if node_attr is None:
            node_attr={}
        if edge_attr is None:
            edge_attr={}
  
        if hasattr(N,'allow_multiedges')==True:
            xgraph=True
        else:
            xgraph=False

        if N.is_directed():
            A = pygraphviz.Agraph(name=N.name,type=pygraphviz.cvar.Agdirected)
            digraph=True
            print "digraph"
	else:
            A = pygraphviz.Agraph(name=N.name,type=pygraphviz.cvar.Agundirected)
            digraph=False

        # set graph attributues            
        A.set_attr(graph_attr)

        # set node attributes            
        for n in N.nodes_iter():
            node=A.add_node(str(n))
            if n in node_attr:
                A.set_node_attr(node,node_attr[n])


        # set edge attributes
        for e in N.edges_iter():
            name=None
            if len(e)==2:
                (u,v)=e
            elif len(e)==3:  # XGraph or XDigraph
                (u,v,x)=e
                if x is not None: 
                    if is_string_like(x): # use data as edge name
                        name=x
            edge=A.add_edge(str(u),str(v),name)
            if xgraph: # if this is an XGraph or XDiGraph
                if isinstance(x,dict): # and the data looks like a dict
                    A.set_edge_attr((u,v),x)  # use that as the attributes
            # now apply the edge attributes from calling argument
            if (u,v) in edge_attr: 
                A.set_edge_attr((u,v),edge_attr[(u,v)])
            if not digraph:                    
                if (v,u) in edge_attr:
                    A.set_edge_attr((v,u),edge_attr[(v,u)])
                        
        return A

def networkx_from_pygraphviz(A, create_using=None,
                             graph_attr=None,
                             node_attr=None,
                             edge_attr=None):
	"""Creates an networkx graph from an pygraphviz graph A"""
        import networkx

        if create_using is None:
            if A.is_undirected():
                create_using=networkx.Graph()
            else:
                create_using=networkx.DiGraph()

        N=networkx.empty_graph(0,create_using)

        if hasattr(N,'allow_multiedges')==True:
            xgraph=True
        else:
            xgraph=False

        N.name=str(A)

        if graph_attr is not None:
            graph_attr.update(A.get_all_attr())
        edges_seen = {}
        for node in A.nodes():
            name=pygraphviz.agnameof(node.anode)
            N.add_node(name)
            if node_attr is not None:
                node_attr[name]=A.get_all_attr(node=node)
        for edge in A.edges():
            if edge in edges_seen:
                continue
            source=pygraphviz.agnameof(edge.source().anode)
            target=pygraphviz.agnameof(edge.target().anode)
            edges_seen[edge]=1
            if edge_attr is not None:
                N.add_edge(source,target)
                edge_attr[(source,target)]=A.get_all_attr(edge=(source,target))
            elif xgraph:
                N.add_edge(source,target,A.get_all_attr(edge=(source,target)))
            else:
                N.add_edge(source,target)
	return N

def graphviz_layout(G,prog='neato',root=None, args=''):
    """
    Create layout using graphviz.
    Returns a dictionary of positions keyed by node.

    >>> from networkx import *
    >>> G=petersen_graph()
    >>> pos=graphviz_layout(G)
    >>> pos=graphviz_layout(G,prog='dot')
    
    This is a wrapper for pygraphviz_layout.

    """
    return pygraphviz_layout(G,prog=prog,root=root,args=args)

def pygraphviz_layout(G,prog='neato',root=None, args=''):
    """
    Create layout using pygraphviz and graphviz.
    Returns a dictionary of positions keyed by node.

    >>> from networkx import *
    >>> G=petersen_graph()
    >>> pos=pygraphviz_layout(G)
    >>> pos=pygraphviz_layout(G,prog='dot')
    
    """
    import tempfile
    try:
        import pygraphviz
    except:
        print "Import Error: not able to import pygraphviz."
        raise

    if root is not None :
        args+=" -Groot=%s"%str(root)

    gprogs=dict.fromkeys(['neato','dot','twopi','circo','fdp','circa'],True)
    try:
        gprogs[prog]==True
    except:
        raise "program %s not from graphviz"%prog 
    
    try: # user must pick one of the graphviz programs...
        runprog = _which(prog)
    except:
        raise "program %s not found in path"%prog 

    tmp_fd, tmp_name = tempfile.mkstemp()
    write_dot(G, tmp_name)
    os.close(tmp_fd)
    cmd=' '.join([runprog,args,"-Tdot",tmp_name])
    stdin,stdout,stderr=os.popen3(cmd, 'b')
    try:
        A=pygraphviz.Agraph()
        A.read(stdout)
        stdin.close(); stdout.close(); stderr.close()
    except:
        print "Graphviz layout with %s failed"%(prog)
        print "the file %s might have useful information"%tmp_name
        print stderr.read()
        stdin.close(); stdout.close(); stderr.close()
        return

    os.unlink(tmp_name)
    node_pos={}
    for n in G.nodes():
        node=A.get_node(str(n))
        try:
            xx,yy=node.get_attr("pos").split(',')
            node_pos[n]=(float(xx),float(yy))
        except:
            print "no position for node",n
            node_pos[n]=(0.0,0.0)
    return node_pos

def _which(name):
    """searches for executable in path """
    import os
    import glob
    paths = os.environ["PATH"]
    for path in paths.split(os.pathsep):
        match=glob.glob(os.path.join(path, name))
        if match:
            return match[0]
    raise "no prog %s in path"%name        

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/drawing/nx_pygraphviz.txt',package='networkx')
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
    
