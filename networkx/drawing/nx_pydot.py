"""
Import and export networkx networks to dot format using pydot.

References:
 - pydot Homepage: http://www.dkbza.org/pydot.html
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
import sys
from string import split
try:
    import pydot
except ImportError:
#    print "Import Error: not able to import Python module pydot."
    raise


def write_dot(G,path=False):
    """Write G to a graphviz dot file."""
    P=pydot_from_networkx(G)
    if path:
        P.write_dot(path)
    else:
        print P.to_string() # write on stdout
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

    data=fh.read()        
    P=pydot.graph_from_dot_data(data)
    return networkx_from_pydot(P)


def pydot_from_networkx(N):
	"""Creates a pydot graph from an networkx graph N"""
	# node_orig = 1

        if N.is_directed():

		graph = pydot.Dot(graph_type='digraph')
	else:
		graph = pydot.Dot(graph_type='graph')

        for v in N.nodes_iter():
            graph.add_node(pydot.Node(str(v)))
        for e in N.edges_iter():
            if len(e)==2:
                (u,v)=e
                graph.add_edge(pydot.Edge(str(u),str(v)))
            if len(e)==3:
                (u,v,x)=e
                graph.add_edge(pydot.Edge(str(u),str(v),label=str(x)))

        # FIXME - add properties from networkx to pydot graph?
        # a nice feature would be to add node positions to pydot graph.
        return graph

def networkx_from_pydot(D, result=False):
	"""Creates an networkx graph from an pydot graph D"""
        import networkx

        if result:
            N=result
        else:
            if D.get_type()=="digraph":
                N=networkx.DiGraph()
            else:
                N=networkx.Graph()
                
        N.name="%s"%(D.graph_name)

        for p in D.node_list:
            N.add_node(p.name)

        edges_seen = {}
        for e in D.edge_list:
            if e in edges_seen:
                continue
            N.add_edge(e.src,e.dst)
            edges_seen[e]=1

        # FIXME - add properties from pydot to networkx?
	return N

def pydot_layout(G,**kwds):
    """
    Create layout using pydot and graphviz.
    Returns a dictionary of positions keyed by node.

    >>> pos=pydot_layout(G)
    >>> pos=pydot_layout(G,prog="twopi")
    
    """
    from networkx.drawing.nx_pydot import pydot_from_networkx
    try:
        import pydot
    except:
        print "Import Error: not able to import pydot."
        raise
    prog = kwds.get('prog', "neato")
    P=pydot_from_networkx(G)
    root = kwds.get('root', None)
    if root!=None :
        P.set("root",str(root))
    D=P.create_dot(prog=prog)
    if D=="":  # no data returned
        print "Graphviz layout with %s failed"%(prog)
        print
        print "To debug what happened try:"
        print "P=pydot_from_networkx(G)"
        print "P.write_dot(\"file.dot\")"
        print "And then run %s on file.dot"%(prog)
        return

    Q=pydot.graph_from_dot_data(D)

    node_pos={}
    for n in G.nodes():
        node=Q.get_node(str(n))
        if node.pos != None:
            xx,yy=split(node.pos,",")
            node_pos[n]=(float(xx),float(yy))
    return node_pos

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('../tests/nx_pydot.txt',package='networkx')
    return suite


if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    
