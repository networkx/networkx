#distutils: language = c++
import cython
import numpy as np
cimport numpy as np
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map as um

cdef class Edge:
    cdef public:
        size_t x
        size_t y
        double weight

cdef class Graph:
    cdef public:
        Settings settings
        double[:, ::1] pos
        double[:, ::1] change
        dict edges
        # um[size_t, um[size_t, double]] edges
        double[::1] mass
        double[::1] size
        size_t number_of_nodes


cdef class Settings:
    cdef dict __dict__
    cdef public:
        float jitter_tolerance
        float scaling
        bint distributed_action
        bint strong_gravity
        bint prevent_overlap
        bint dissuade_hubs
        bint edge_weight
        bint linlog

# Utility functions to interface
# with the "fake graph"
cdef double get_mass(size_t node, Graph g)
cdef double get_size(size_t node, Graph g)
cdef double[::1] get_pos(size_t node, Graph g)
cdef double[::1] get_change(size_t node, Graph g)

@cython.locals(out = double[::1], x_pos = double[::1], y_pos = double[::1], idx = size_t)
cdef double[::1] get_difference(size_t x, size_t y, Graph g)

@cython.locals(d = double, delta = double[::1], idx = size_t)
cpdef double get_distance(size_t x, size_t y, Graph g, bint use_weight =*)

@cython.locals(idx = size_t)
cdef void update(size_t node, double[::1] value, Graph g)

cdef class Swing:
    cdef public:
        float  swing
        float effective_traction


ctypedef void(*r_force)(size_t x,
                        size_t y,
                        Graph g,
                        float k,
                        )
ctypedef void(*a_force)(size_t x,
                        size_t y,
                        Graph g,
                        float k,
                        )

@cython.locals(
    dist = cython.float,
    value = double[::1],
)
cdef void linear_attraction(
    size_t x,
    size_t y,
    Graph g,
    float k,
)

@cython.locals(
    d = double,
    d_= double,
    factor = double,
    delta = double[::1]
)
cdef void  linear_repulsion(
    size_t x,
    size_t y,
    Graph g,
    float k,
)


@cython.locals(
    dist = cython.float,
    value = double[::1],
)
cdef void linlog_attraction(
    size_t x,
    size_t y,
    Graph g,
    float k,
)

@cython.locals(
    neighbor = size_t,
)
cdef void apply_attraction(size_t  node,
                            Graph g,
                            a_force attraction,
                            float k,
                           )

@cython.locals(
    current_pos = double[::1],
    discrete_pos = double[::1],
    other = cython.int,
)
cdef void apply_repulsion(
    size_t node,
    Graph g,
    r_force repulsion,
    double k=*,
)


@cython.locals(pos = double[::1],
               d = double,
               mass = double,
               value = double[::1])
cdef void apply_gravity(size_t node,
                  Graph g,
                  double k=*,
                  )


@cython.locals(n = cython.int,
               estimated_jitter_tolerance = cython.float,
               min_jitter = cython.float,
               max_jitter = cython.float,
               tmp = cython.float,
               jitter = cython.float,
               min_speed_efficiency = cython.float,
               target_speed = cython.float,
               z = cython.float,
               maxRise = cython.float,
               node = cython.int,
               change = double[::1],
               pos = double[::1])
cdef tuple apply_forces(Graph g,
                        Swing swing,
                        float speed,
                        float speed_efficiency,
                        float jitter_tolerance)


@cython.locals(pos = cython.dict,
               nodes = long[::1],
               swing = Swing,
               dpos = cython.dict,
               i = cython.int,
               node_pos = double[::1],
               change = double[::1],
               node = cython.int,
               swinging = cython.float,
               node_mas = cython.float,
               attraction_force = a_force,
               repulsion_force = r_force)
cpdef dict forceatlas2(
    object g,
    object pos=*,
    size_t n_iter=*,
    Settings settings=*,
)
