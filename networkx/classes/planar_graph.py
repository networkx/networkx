"""Base class for undirected graphs with planar embedding.

The Graph class allows any hashable, comparable object as a node
and can associate key/value attribute pairs with each undirected edge.

Self-loops are allowed but multiple edges are not.
"""
#    Copyright (C) 2015 by
#    Lukas Barth (mail@tinloaf.de)
#    All rights reserved.
#    BSD license.
from copy import deepcopy
import networkx as nx
from networkx.exception import NetworkXError
import networkx.convert as convert

__author__ = """\n""".join(['Lukas Barth (mail@tinloaf.de)'])

import collections

from ordered import OrderedGraph
from networkx.exception import NetworkXError

class NoPlanarityProvidedException(Exception):
    pass

class InconsistentPlanarityData(Exception):
    pass

class PlanarGraph(OrderedGraph):
    """Class to represent an undirected planar Graph

    This class is used to represent an undirected graph together with a
    (combinatorial) planar embedding. It provides various functions that rely
    on this planar embedding.
    """

    def __init__(self, data=None, **attr):
        self._has_planar_data = {}
        """Stores for every node whether the order of adjacencies has been provided"""
        self._computed_planar = True
        """Indicates whether all internal variables for the current embedding have been computed"""

        self._adjacency_orders = {}
        """Stores for every node the order (in clockwise order) of its adjacencies
        in the given embedding
        """
        self._adjacency_indices = {}
        """Reverse mapping for _adjacency_orders. _adjacency_indices[u][v] indicates the
        index in _adjacency_orders[u] that will be v
        """

        self._next_face_id = 0
        self._left_face = {}
        """When _computed_planar is True, this stores for every edge which face is on
        its left side. Please note that for this purpose, edges are directed towards
        the smaller vertex.
        """
        self._right_face = {}
        """When _computed_planar is True, this stores for every edge which face is on
        its right side. Please note that for this purpose, edges are directed towards
        the smaller vertex.
        """
        self._faces = {}
        """When _computed_planar is True, this stores the vertices along each face in
        clockwise order.
        """
        self._facehashes = {}
        """When recomputing the faces, this is used to check whether a face has not changed.
        In this case, we try to preserve its ID.
        """

        super(PlanarGraph, self).__init__(data=data, **attr)

    def get_face(self, face_id):
        """Returns the vertices that appear on the face identified by face_id,
        in order.

        Faces will be ordered clockwise for inner faces and counterclockwise for
        the outer face."""
        return self._faces[face_id]

    def _planar_data_complete(self):
        return all(self._has_planar_data.values())

    def _grow_face(self, start_edge, u, v):
        index_in_v = self._adjacency_indices[v][u]
        next_index = index_in_v - 1
        if next_index < 0:
            next_index = len(self._adjacency_orders[v]) - 1
        next_vertex = self._adjacency_orders[v][next_index]

        if (v, next_vertex) == start_edge:
            if (u < v):
                return [(u, 0)]
            else:
                return [(u, 1)]

        side = 0 if (u < v) else 1
        return [(u, side)] + self._grow_face(start_edge, v, next_vertex)

    def _canonicalize_face(self, face):
        print("Face before: " + str(face))
        # TODO
        # Decide if we actually need this, or if a rotationally invariant hash is
        # enough?
        canonical = tuple(min(
            face if i == 0 else (face[i:] + face[:i])
            for i in range(len(face))
        ))
        print("Face after: " + str(canonical))
        return canonical

    def _incorporate_face(self, face):
        name = self._canonicalize_face([v for v,side in face])
        if name in self._old_facehashes:
            face_id = self._old_facehashes[name]
        else:
            face_id = self._next_face_id
            self._next_face_id += 1

        self._facehashes[name] = face_id
        self._faces[face_id] = name

        face_edges = ((face[i][0], face[(i+1) % len(face)][0], face[i][1]) for i in range(0, len(face)))
        face_edges = list(face_edges)

        for u,v,side in face_edges:
            if side == 0:
                self._left_face[frozenset((u,v))] = face_id
            else:
                self._right_face[frozenset((u,v))] = face_id

    def _create_faces(self):
        self._left_face = {}
        self._right_face = {}
        self._old_faces = self._faces
        self._faces = {}
        self._old_facehashes = self._facehashes
        self._facehashes = {}

        for (u,v) in self.edges():
            if not frozenset((u,v)) in self._left_face:
                if (u < v):
                    new_face = self._grow_face((u, v), u, v)
                else:
                    new_face = self._grow_face((v, u), v, u)

                #new_face = tuple(reversed(new_face))
                self._incorporate_face(new_face)

            if not frozenset((u,v)) in self._right_face:
                if (u < v):
                    new_face = self._grow_face((v, u), v, u)
                else:
                    new_face = self._grow_face((u, v), u, v)

                #new_face = tuple(reversed(new_face))
                self._incorporate_face(new_face)

        del self._old_faces
        del self._old_facehashes

    def _order_vertices(self):
        for v in self.nodes():
            old_adj = self.adj[v]
            self.adj[v] = collections.OrderedDict()
            for neigh in self._adjacency_orders[v]:
                self.adj[v][neigh] = old_adj[neigh]

    def _compute_planarity(self):
        if not self._planar_data_complete():
            raise NoPlanarityProvidedException()

        self._create_faces()
        self._order_vertices()

        self._computed_planar = True

    def __getitem__(self, n):
        if not self._computed_planar:
            self._compute_planarity()
        return super(PlanarGraph, self).__getitem__(n)

    def get_face_between(self, base, u, v):
        """Returns the face between the edges (base,u) and (base,v).

        Please note that this means that u and v must be consecutive (in
        clockwise order) neighbors of base.
        """
        if not self._computed_planar:
            self._compute_planarity()

        u_index = self._adjacency_indices[base].get(u, None)
        if u_index is None:
            raise NetworkXError("No edge base-u")

        v_index = self._adjacency_indices[base].get(v, None)
        if v_index is None:
            raise NetworkXError("No edge base-v")

        if v_index - u_index != 1 and not (u_index == len(self._adjacency_orders[base])-1 and v_index == 0):
            print(self._adjacency_orders[base])
            raise NetworkXError("u and v are not consecutive neighbors of base")

        if base < u: # incoming edge
            face = self._left_face[frozenset((base,u))]
        else:
            face = self._right_face[frozenset((base,u))]

        return face

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
        """Inserts an edge at a given position within the combinatorial embedding.

        Arguments:
            u:          One end of the edge
            u_pos:      The index inside u's adjacencies that this edge will be insertred at.
                        I.e. this edge will be between old adjacencies (u_pos-1) andd u_pos
                        of u.
            v:          Other end of the edge
            v_pos:      Same as u_pos, only for v
            attr_dict:  Atrribute data for this edge
        """
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
        """Can be used to provide the order of adjacencies around a vertex, in
        clockwise order.

        This must be done for every vertex before planarity-related methods can
        be used!

        Example:
            If vertex 0 has neighbors 1, 2 and 3 (in this order), this would be
            correct:
                G.provide_planarity_data(0, [1,2,3])
            Equally correct would be:
                G.provide_planarity_data(0, [2,3,1])
        """
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
