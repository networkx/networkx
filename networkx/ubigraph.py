"""
Base classes for interaction between NetworkX and Ubigraph.

These classes allow drawing with Ubigraph and all of the NetworkX functions.

Examples
--------
(start Ubigraph server)
>>> import networkx
>>> G=networkx.UbiGraph()
>>> G.add_edge('a','b',color='#0000ff') # blue edge between 'a' and 'b'

>>> G=networkx.UbiGraph(networkx.cycle_graph(5)) # cycle of length 5

See the examples 
https://networkx.lanl.gov/browser/networkx/trunk/doc/examples/ubigraph

UbiGraph 
--------
NetworkX compatible graph class.  Allows self loops and multiple edges.  
Extends to NetworkX XGraph class. 

UbiDiGraph 
--------
NetworkX compatible digraph class.  Allows self loops and multiple edges.  
Extends NetworkX XDiGraph class. 

Ubigraph attributes
--------------------
In addition to all of the XGraph and XDiGraph methods and NetworkX functions
this class also provides methods to set node and edge attributes and styles.

Node and edge attributes:

>>> G=networkx.UbiGraph()
>>> G.add_node('a',shape='torus')
>>> G.add_edge('a','b',style='dashed')
>>> G.set_node_attr('a',color='#0000ff') # node a blue
>>> G.set_node_attr(color='#00ffff') # all nodes green

Node and edge styles:

>>> G=networkx.UbiGraph(networkx.cycle_graph(5)) # cycle of length 5
>>> redtorus=G.new_node_style(color="#ff0000',shape='torus')
>>> G.set_node_attr(style=redtorus) # all nodes to redtorus style

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

from networkx.xgraph import XGraph
from networkx.xdigraph import XDiGraph
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert

class UbiGraph(XGraph):
    def __init__(self, data=None, name='', 
                 selfloops=False, 
                 multiedges=False, 
                 ubigraph_server= 'http://127.0.0.1:20738/RPC2',
                 clear=True,
                 nextid=0):

        import xmlrpclib
        try:
            server_url = ubigraph_server
            self.server = xmlrpclib.Server(server_url)
            self.ubigraph = self.server.ubigraph
            if clear:
                self.ubigraph.clear()
        except:
            raise IOError("No Ubigraph server found")
        
        # default node and edge styles
        self.ubigraph.set_vertex_style_attribute(0, "color", "#ff0000")
        self.ubigraph.set_vertex_style_attribute(0, "shape", "sphere")
        self.ubigraph.set_vertex_style_attribute(0, "size", "0.7")

        self.ubigraph.set_edge_style_attribute(0, "color", "#ffffff")
        self.ubigraph.set_edge_style_attribute(0, "width", "2.0")

        self.use_splines=False
        self.use_node_labels=False
        self.use_edge_labels=False

        # keep a mapping from nodes to ubigraph ids
        self.nodeid={} 
        self.nextid=nextid
        self.idnode={} 



        self.adj={}      # adjacency list
        self.selfloops=selfloops
        self.multiedges=multiedges
        if data is not None:
            self=convert.from_whatever(data,create_using=self)
        self.name=name


    def add_node(self, n,**kwds):
        if n not in self:
            XGraph.add_node(self,n)
            self.nodeid[n]=self.nextid
            self.idnode[self.nextid]=n
            self.nextid+=1
            self.ubigraph.new_vertex_w_id(self.nodeid[n])
            # add ubigraph attributes
            for (k,v) in kwds.items():
                ret=self.ubigraph.set_vertex_attribute(self.nodeid[n],k,v) 
            # support toggling node labels
            if self.use_node_labels:
                self.ubigraph.set_vertex_attribute(self.nodeid[n],'label',str(n))

    def add_nodes_from(self, nlist,**kwds):
        for n in nlist:
            self.add_node(n,**kwds)


    def delete_node(self,n):
        if n in self:
            XGraph.delete_node(self,n)
            self.ubigraph.remove_vertex(self.nodeid[n])
            id=self.nodeid[n]
            del self.nodeid[n]
            del self.idnode[id]


    def delete_nodes_from(self,nlist):
        for n in nlist:
            self.delete_node(n)


    def add_edge(self, u, v=None, x=None, **kwds):  
        if v is None: # add_edge was called as add_edge(e), with  e=(u,v,x)
            if len(u)==3: # case e=(u,v,x)
                u,v,x=u
            else:          # assume e=(u,v)
                u,v=u   # x=None

        # if edge exists, quietly return if multiple edges are not allowed
        if not self.multiedges and self.has_edge(u,v,x):
            return

        # add nodes            
        self.add_node(u)
        self.add_node(v)

        # self loop? quietly return if not allowed
        if not self.selfloops and u==v: 
            return

        # create ubigraph edge
        # build dictionary with edge id and user data to use as edge data
        e=self.ubigraph.new_edge(self.nodeid[u],self.nodeid[v])
        edata={'id':e,'data':x}

        if self.multiedges: # add x to the end of the list of objects
                            # that defines the edges between u and v
            self.adj[u][v]=self.adj[u].get(v,[])+ [edata]
            if u!=v:
                self.adj[v][u]=self.adj[v].get(u,[])+ [edata]
        else:  # x is the new object assigned to single edge between u and v
            self.adj[u][v]=edata
            if u!=v:
                self.adj[v][u]=edata # a copy would be required to avoid
                                   # modifying both at the same time
                                   # when doing a delete_edge
        # add ubigraph attributes
        for (k,v) in kwds.items():
            ret=self.ubigraph.set_vertex_attribute(e,k,v) 

        # support toggling edge labels
        if self.use_edge_labels:
            self.ubigraph.set_edge_attribute(e,'label',str(x))

    def add_edges_from(self, ebunch,**kwds):  
        for e in ebunch:
            self.add_edge(e,**kwds)

    def delete_edge(self, u, v=None, x=None): 
        if v is None:      # was called as delete_edge(e)
            if len(u)==3:  # case e=(u,v,x)
                u,v,x=u
            else:           # assume e=(u,v), x unspecified, set to None
                u,v=u    # x=None
        try:
            xdata=x['data']
        except:
            xdata=x

        if self.multiedges:
            if (self.adj.has_key(u) and self.adj[u].has_key(v)):
                x=None
                for edata in self.adj[u][v]:
                    if xdata == edata['data']:
                        x=edata # (u,v,edata) is an edge
                        eid=edata['id']
                if x is None: 
                    return # no edge
                # remove the edge item from list
                self.adj[u][v].remove(x)  
                # and if not self loop remove v->u entry
                if u!=v:                   
                    self.adj[v][u].remove(x) 
                # if last edge between u and v was deleted, remove all trace
                if len(self.adj[u][v])==0:
                    del self.adj[u][v]      
                    # and if not self loop remove v->u entry
                    if u!=v:              
                        del self.adj[v][u] 
                self.ubigraph.remove_edge(eid)
        else:  # delete single edge       
            if self.has_neighbor(u,v):
                eid=self.get_edge(u,v)['id']                    
                self.ubigraph.remove_edge(eid)
                del self.adj[u][v]
                if u!=v:
                    del self.adj[v][u]


    def delete_edges_from(self, ebunch): 
        for e in ebunch:
            self.delete_edge(e)

    def clear(self):
        if len(self)>0:
            XGraph.clear(self)
            self.ubigraph.clear()
            self.nodeid={}
            self.nextid=0

# node and edge attrs            
            
    def set_node_attr(self,nbunch=None,style=None,**kwds):
        bunch=self.prepare_nbunch(nbunch)
        for n in bunch:
            if style is None:
                for (k,v) in kwds.items():
                    ret=self.ubigraph.set_vertex_attribute(self.nodeid[n],k,v) 
            else:
                self.ubigraph.change_vertex_style(self.nodeid[n],style) 

    def set_edge_attr(self,ebunch=None,style=None,**kwds):
        if ebunch is None:
            bunch=self.edges()
        else:
            try:
                self.has_edge(ebunch)
                bunch=[ebunch]
            except:
                bunch=list(ebunch)

        for (u,v,d) in bunch:
            if style is None:
                for (k,v) in kwds.items():
                    ret=self.ubigraph.set_edge_attribute(d['id'],k,v) 
            else:
                ret=self.ubigraph.change_edge_style(d['id'],style) 

# node and edge styles                

    def new_node_style(self,style=0,**kwds):
        style=self.ubigraph.new_vertex_style(style)
        for (k,v) in kwds.items():
            self.ubigraph.set_vertex_style_attribute(style,k,v) 
        return style


    def new_edge_style(self,style=0,**kwds):
        style=self.ubigraph.new_edge_style(style)
        for (k,v) in kwds.items():
            self.ubigraph.set_edge_style_attribute(style,k,v) 
        return style


# ubigraph helper methods
# an interface to the internal ubigraph methods that do this
# would make this simpler

    def splines(self):
        """Toggle spline edges.
        """
        if self.use_splines==True:
            self.set_edge_attr(spline='false')
            self.use_splines=False
        else:
            self.set_edge_attr(spline='true')
            self.use_splines=True


    def node_labels(self,nbunch=None,labels=None):
        """Toggle node labels.
        """
        bunch=list(self.prepare_nbunch(nbunch))
        if self.use_node_labels==True:
            labels=dict(zip(bunch,['']*len(bunch)))
            self.use_node_labels=False
        else:
            if labels is None:
                  labels=dict(zip(bunch,bunch))
            self.use_node_labels=True
        for n,label in labels.items():
            self.ubigraph.set_vertex_attribute(self.nodeid[n],'label',str(label))
    
    def edge_labels(self,ebunch=None,labels=None):
        """Toggle edge labels.
        """
        if ebunch is None:
            bunch=self.edges()
        else:
            try:
                self.has_edge(ebunch)
                bunch=[ebunch]
            except:
                bunch=list(ebunch)

        if self.use_edge_labels==True:
            labels=dict([(d['id'],'') for u,v,d in bunch])
            self.use_edge_labels=False
        else:
            if labels is None:
                  labels=dict([(d['id'],str(d['data'])) for u,v,d in bunch if d['data'] is not None])
            self.use_edge_labels=True
        for eid,label in labels.items():
            self.ubigraph.set_edge_attribute(eid,'label',label)

class UbiDiGraph(UbiGraph,XDiGraph):
    def __init__(self, data=None, name='', 
                 selfloops=False, 
                 multiedges=False, 
                 ubigraph_server= 'http://127.0.0.1:20738/RPC2',
                 clear=True):


        self.pred={}        # predecessor
        self.succ={}

        UbiGraph.__init__(self,
                          data=data,name=name,
                          selfloops=selfloops,
                          multiedges=multiedges,
                          ubigraph_server=ubigraph_server,
                          clear=clear)
        self.ubigraph.set_edge_style_attribute(0, "arrow", "true")

        self.adj=self.succ  # successor is same as adj for digraph


    def add_node(self, n,**kwds):
        if n not in self:
            XDiGraph.add_node(self,n)
            self.nodeid[n]=self.nextid
            self.nextid+=1
            self.ubigraph.new_vertex_w_id(self.nodeid[n])
            # add ubigraph attributes
            for (k,v) in kwds.items():
                ret=self.ubigraph.set_vertex_attribute(self.nodeid[n],k,v) 
            # support toggling node labels
            if self.use_node_labels:
                self.ubigraph.set_vertex_attribute(self.nodeid[n],'label',str(n))

    def delete_node(self,n):
        if n in self:
            XDiGraph.delete_node(self,n)
            self.ubigraph.remove_vertex(self.nodeid[n])


    def add_edge(self, u, v=None, x=None, **kwds):  
        if v is None: # add_edge was called as add_edge(e), with e a tuple
            if len(u)==3: #case e=(u,v,x)
                u,v,x=u
            else:          # assume e=(u,v)
                u,v=u   # x=None

        # if edge exists, quietly return if multiple edges are not allowed
        if not self.multiedges and self.has_edge(u,v,x):
            return

        # add nodes            
        self.add_node(u)
        self.add_node(v)

        # self loop? quietly return if not allowed
        if not self.selfloops and u==v: 
            return

        # create ubigraph edge
        # build dictionary with edge id and user data to use as edge data
        e=self.ubigraph.new_edge(self.nodeid[u],self.nodeid[v])
        edata={'id':e,'data':x}

        if self.multiedges: # append x to the end of the list of objects
                            # that defines the edges between u and v
            self.succ[u][v]=self.succ[u].get(v,[])+ [edata]
            self.pred[v][u]=self.pred[v].get(u,[])+ [edata]
        else:  # x is the new object assigned to single edge between u and v
            self.succ[u][v]=edata
            self.pred[v][u]=edata # note that the same object is referred to
                                # from both succ and pred
        for (k,v) in kwds.items():
            ret=self.ubigraph.set_edge_attribute(e,k,v) 

        # support toggling edge labels
        if self.use_edge_labels:
            self.ubigraph.set_edge_attribute(e,'label',str(x))


    def delete_edge(self, u, v=None, x=None): 
        if v is None:      # was called as delete_edge(e)
            if len(u)==3:  # case e=(u,v,x)
                u,v,x=u
            else:           # assume e=(u,v), x unspecified, set to None
                u,v=u    # x=None
        try:
            xdata=x['data']
        except:
            xdata=x

        if self.multiedges:              # multiedges are stored as a list
            if (self.succ.has_key(u) and self.succ[u].has_key(v)):
                x=None
                for edata in self.succ[u][v]:
                    if xdata == edata['data']:
                        x=edata # (u,v,edata) is an edge
                        eid=edata['id']
                if x is None: 
                    return # no edge
                self.succ[u][v].remove(x)  # remove the edge item from list
                self.pred[v][u].remove(x)
                if len(self.succ[u][v])==0: # if last edge between u and v
                    del self.succ[u][v]     # was deleted, remove all trace
                    del self.pred[v][u]
                self.ubigraph.remove_edge(eid)
        else:  # delete single edge
            if self.has_successor(u,v):
                eid=self.get_edge(u,v)['id']                    
                self.ubigraph.remove_edge(eid)
                del self.succ[u][v]
                del self.pred[v][u]
        return

    def clear(self):
        if len(self)>0:
            XDiGraph.clear(self)
            self.ubigraph.clear()
            self.nodeid={}
            self.nextid=0

