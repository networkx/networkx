from ordered import OrderedGraph

class NoPlanarityProvidedException(Exception):
    pass

class InconsistentPlanarityData(Exception):
    pass

class PlanarGraph(OrderedGraph):
    def __init__(self, data=None, **attr):
        self._has_planar_data = {}
        self._computed_planar = True

        self._adjacency_orders = {}
        self._adjacency_indices = {}

        super(PlanarGraph, self).__init__(data=data, **attr)

    def _planar_data_complete(self):
        return all(self._has_planar_data.values())

    def _compute_planarity(self):
        if not self._planar_data_complete():
            raise NoPlanarityProvidedException()

        self._computed_planar = True

    def __getitem__(self, n):
        if not self._computed_planar:
            self._compute_planarity()
        return super(PlanarGraph, self).__getitem__(n)

    def add_node(self, n, attr_dict=None, **attr):
        if n not in self.node:
            self._has_planar_data[n] = True
            self._adjacency_orders[n] = []
            self._adjacency_indices[n] = {}

        super(PlanarGraph, self).add_node(n, attr_dict=attr_dict, **attr)

    def add_nodes_from(self, nodes, **attr):
        for n in nodes:
            try:
                if n not in self.node:
                    self._has_planar_data[n] = True
                    self._adjacency_orders[n] = []
                    self._adjacency_indices[n] = {}
            except TypeError:
                nn, ndict = n
                if nn not in self.node:
                    self._has_planar_data[nn] = True
                    self._adjacency_orders[nn] = []
                    self._adjacency_indices[nn] = {}

        super(PlanarGraph, self).add_nodes_from(nodes, **attr)

    def remove_node(self, n):
        print("Removing " + str(n))
        adjs = list(self.adj[n].keys())

        super(PlanarGraph, self).remove_node(n)

        del self._has_planar_data[n]
        if n in self._adjacency_orders:
            del self._adjacency_orders[n]
        if n in self._adjacency_indices:
            del self._adjacency_indices[n]

        for neighbor in adjs:
            if neighbor == n:
                continue

            if self._has_planar_data[neighbor]:
                n_index = self._adjacency_indices[neighbor][n]
                del self._adjacency_orders[neighbor][n_index]
                del self._adjacency_indices[neighbor][n]
                for moved in self._adjacency_orders[neighbor][n_index:]:
                    self._adjacency_indices[neighbor][moved] -= 1

    def remove_nodes_from(self, nodes):
        ''' TODO this differs from graph! '''
        for node in nodes:
            if not node in self.node:
                continue
            self.remove_node(node)

    def add_edge(self, u, v, attr_dict=None, **attr):
        super(PlanarGraph, self).add_edge(u, v, attr_dict=attr_dict, **attr)
        self._has_planar_data[u] = False
        self._has_planar_data[v] = False
        self._computed_planar = False

    def insert_edge(self, u, u_pos, v, v_pos, attr_dict=None, **attr):
        super(PlanarGraph, self).add_edge(u, v, attr_dict=attr_dict, **attr)

        if self._has_planar_data[u]:
            self._adjacency_orders[u].insert(u_pos, v)
            self._adjacency_indices[u][v] = u_pos
            for moved in self._adjacency_orders[u][(u_pos+1):]:
                self._adjacency_indices[u][moved] += 1

        if self._has_planar_data[v]:
            self._adjacency_orders[v].insert(v_pos, u)
            self._adjacency_indices[v][u] = v_pos
            for moved in self._adjacency_orders[v][(v_pos+1):]:
                self._adjacency_indices[v][moved] += 1

        self._computed_planar = False

    def provide_planarity_data(self, v, ordered_adjacencies):
        if not len(set(ordered_adjacencies)) == len(ordered_adjacencies):
            raise InconsistentPlanarityData()
        if not set(ordered_adjacencies) == set(self.adj[v].keys()):
            raise InconsistentPlanarityData()

        self._adjacency_orders[v] = ordered_adjacencies
        self._adjacency_indices[v] = {}
        for i in range(0,len(ordered_adjacencies)):
            self._adjacency_indices[v][ordered_adjacencies[i]] = i

        self._has_planar_data[v] = True
        self._computed_planar = False

    def add_edges_from(self, ebunch, attr_dict=None, **attr):
        super(PlanarGraph, self).add_edges_from(ebunch, attr_dict=attr_dict, **attr)

        for e in ebunch:
            u, v = e[:2]

            self._has_planar_data[u] = False
            self._has_planar_data[v] = False
            self._computed_planar = False

    def remove_edge(self, u, v):
        super(PlanarGraph, self).remove_edge(u,v)

        if self._has_planar_data[u]:
            v_index = self._adjacency_indices[u][v]
            del self._adjacency_orders[u][v_index]
            del self._adjacency_indices[u][v]

        if self._has_planar_data[v]:
            u_index = self._adjacency_indices[v][u]
            del self._adjacency_orders[v][u_index]
            del self._adjacency_indices[v][u]

    def remove_edges_from(self, ebunch):
        """ TODO differs from graph """

        for e in ebunch:
            u, v = e[:2]
            if not v in self.adj[u]:
                continue
            self.remove_edge(u, v)

    def neighbors(self, n):
        if not self._computed_planar:
            self._compute_planarity()
        return super(PlanarGraph, self).neighbors(n)

    def neighbors_iter(self, n):
        if not self._computed_planar:
            self._compute_planarity()
        return super(PlanarGraph, self).neighbors_iter(n)

    def adjacency_list(self):
        if not self._computed_planar:
            self._compute_planarity()
        return super(PlanarGraph, self).adjacency_list()

    def adjacency_iter(self):
        if not self._computed_planar:
            self._compute_planarity()
        return super(PlanarGraph, self).adjacency_iter()

    def clear(self):
        super(PlanarGraph, self).clear()
        self._has_planar_data = {}
        self._computed_planar = True
        self._adjacency_orders = {}
        self._adjacency_indices = {}

    def to_directed(self):
        raise NotImplementedError()

    def subgraph(self, nbunch):
        raise NotImplementedError()
