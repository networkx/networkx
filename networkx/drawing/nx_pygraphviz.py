"""
Import and export networkx networks to dot format using pygraphviz.

Provides:

 - write_dot()
 - read_dot()
 - graphviz_layout()
 - pygraphviz_layout()

 - pygraphviz_from_networkx()
 - networkx_from_pygraphviz()

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


def pygraphviz_from_networkx(N):
	"""Creates a graphviz graph from an networkx graph N"""
	# node_orig = 1

        if N.is_directed():
            A = pygraphviz.Agraph(type=pygraphviz.cvar.Agdirected)
	else:
            A = pygraphviz.Agraph(type=pygraphviz.cvar.Agundirected)

        for v in N.nodes_iter():
            n=A.add_node(str(v))
        for e in N.edges_iter():
            if len(e)==2:
                (u,v)=e
                e=A.add_edge(str(u),str(v),str(u)+str(v))
            elif len(e)==3:
                (u,v,x)=e
                e=A.add_edge(str(u),str(v),str(x))

        # FIXME - add properties from networkx to pydot graph?
        # a nice feature would be to add node positions to pydot graph.
        return A

def networkx_from_pygraphviz(A, create_using=None):
	"""Creates an networkx graph from an pygraphviz graph A"""
        import networkx

        if create_using is None:
            if A.is_undirected():
                create_using=networkx.Graph()
            else:
                create_using=networkx.DiGraph()

        N=networkx.empty_graph(0,create_using)

        N.name="from pygraphviz"

        edges_seen = {}
        for node in A.nodes():
            name=pygraphviz.agnameof(node.anode)
            N.add_node(name)
        for edge in A.edges():
            if edge in edges_seen:
                continue
            source=pygraphviz.agnameof(edge.source().anode)
            target=pygraphviz.agnameof(edge.target().anode)
            edges_seen[edge]=1
            N.add_edge(source,target)

        # FIXME - add properties from pygraphviz to networkx?
	return N

def graphviz_layout(G,prog='neato',root=None, args=''):
    """
    Create layout using graphviz.
    Returns a dictionary of positions keyed by node.

    >>> pos=graphviz_layout(G)
    >>> pos=graphviz_layout(G,prog='dot')
    
    This is a wrapper for pygraphviz_layout.

    """
    return pygraphviz_layout(G,prog=prog,root=root,args=args)

def pygraphviz_layout(G,prog='neato',root=None, args=''):
    """
    Create layout using pygraphviz and graphviz.
    Returns a dictionary of positions keyed by node.

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
    
