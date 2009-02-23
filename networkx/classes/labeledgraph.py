from graph import Graph
from digraph import DiGraph
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert

class LabeledGraph(Graph):
    def __init__(self, data=None, name='', weighted=True):
        super(LabeledGraph,self).__init__(data,name,weighted)
        # node labels
        if hasattr(data,'label') and isinstance(data.label,'dict'):
            self.label=data.label.copy()
        else:
            self.label = {} 
        
    def add_node(self, n, data=None):
        super(LabeledGraph,self).add_node(n)
        if data is not None:
            self.label[n]=data

    def add_nodes_from(self, nbunch, data=None):
        for nd in nbunch:
            try:
                n,data=nd
            except (TypeError,ValueError):
                n=nd
                data=None
            self.add_node(n,data)
        
    def remove_node(self, n):
        super(LabeledGraph,self).remove_node(n)
        try:
            del self.label[n]
        except KeyError:
            pass

    def remove_nodes_from(self, nbunch):
        for n in nbunch:
            self.remove_node(n)

    def nodes_iter(self, nbunch=None, data=False):
        if nbunch is None:
            nbunch=self.adj.iterkeys()
        else:
            nbunch=self.nbunch_iter(nbunch)
        if data:
            for n in nbunch:
                data=self.label.get(n,None)
                yield (n,data)
        else:
            for n in nbunch:            
                yield n

    def nodes(self, nbunch=None, data=False):
        if data:    
            return dict(self.nodes_iter(nbunch,data))
        else:       
            return list(self.nodes_iter(nbunch))

    def get_node(self, n):
        if n not in self.adj:
            raise NetworkXError("node %s not in graph"%(n,))
        else:
            data=self.label.get(n,None)            
        return data
            
    def clear(self):
        super(LabeledGraph,self).clear()
        self.label={}

    def subgraph(self, nbunch, copy=True):
        H=super(LabeledGraph,self).subgraph(nbunch, copy)
        H.label=dict( (k,v) for k,v in self.label.items() if k in H)        
        return H

    def to_directed(self):
        H=super(LabeledGraph,self).to_directed()
        H.label=dict( (k,v) for k,v in self.label.items() if k in H)        
        return H



class LabeledDiGraph(LabeledGraph,DiGraph):
    pass  # just use the inherited classes
