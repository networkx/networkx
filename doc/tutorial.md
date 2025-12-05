---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Tutorial

```{currentmodule} networkx

```

This guide can help you start working with NetworkX.

## Creating a graph

Create an empty graph with no nodes and no edges.

```{code-cell}
import networkx as nx
G = nx.Graph()
```

By definition, a {class}`Graph` is a collection of nodes (vertices) along with
identified pairs of nodes (called edges, links, etc). In NetworkX, nodes can
be any {py:term}`hashable` object e.g., a text string, an image, an XML object,
another Graph, a customized node object, etc.

```{note}
Python's `None` object is not allowed to be used as a node. It
determines whether optional function arguments have been assigned in many
functions.
```

## Nodes

The graph `G` can be grown in several ways. NetworkX includes many
{doc}`graph generator functions <reference/generators>` and
{doc}`facilities to read and write graphs in many formats <reference/readwrite/index>`.
To get started though we'll look at simple manipulations. You can add one node
at a time,

```{code-cell}
G.add_node(1)
```

or add nodes from any {py:term}`iterable` container, such as a list

```{code-cell}
G.add_nodes_from([2, 3])
```

You can also add nodes along with node
attributes if your container yields 2-tuples of the form
`(node, node_attribute_dict)`:

```{code-cell}
G.add_nodes_from([(4, {"color": "red"}), (5, {"color": "green"})])
```

Node attributes are discussed further {ref}`below <attributes>`.

Nodes from one graph can be incorporated into another:

```{code-cell}
H = nx.path_graph(10)
G.add_nodes_from(H)
```

`G` now contains the nodes of `H` as nodes of `G`.
In contrast, you could use the graph `H` as a node in `G`.

```{code-cell}
G.add_node(H)
```

The graph `G` now contains `H` as a node. This flexibility is very powerful as
it allows graphs of graphs, graphs of files, graphs of functions and much more.
It is worth thinking about how to structure your application so that the nodes
are useful entities. Of course you can always use a unique identifier in `G`
and have a separate dictionary keyed by identifier to the node information if
you prefer.

```{note}
You should not change the node object if the hash depends on its contents.
```

## Edges

`G` can also be grown by adding one edge at a time,

```{code-cell}
G.add_edge(1, 2)
e = (2, 3)
G.add_edge(*e)  # unpack edge tuple*
```

by adding a list of edges,

```{code-cell}
G.add_edges_from([(1, 2), (1, 3)])
```

or by adding any {term}`ebunch` of edges. An _ebunch_ is any iterable
container of edge-tuples. An edge-tuple can be a 2-tuple of nodes or a 3-tuple
with 2 nodes followed by an edge attribute dictionary, e.g.,
`(2, 3, {'weight': 3.1415})`. Edge attributes are discussed further
{ref}`below <attributes>`.

```{code-cell}
G.add_edges_from(H.edges)
```

There are no complaints when adding existing nodes or edges. For example,
after removing all nodes and edges,

```{code-cell}
G.clear()
```

we add new nodes/edges and NetworkX quietly ignores any that are
already present.

```{code-cell}
G.add_edges_from([(1, 2), (1, 3)])
G.add_node(1)
G.add_edge(1, 2)
G.add_node("spam")        # adds node "spam"
G.add_nodes_from("spam")  # adds 4 nodes: 's', 'p', 'a', 'm'
G.add_edge(3, 'm')
```

At this stage the graph `G` consists of 8 nodes and 3 edges, as can be seen by:

```{code-cell}
G.number_of_nodes()
```

```{code-cell}
G.number_of_edges()
```

```{note}
The order of adjacency reporting (e.g., {meth}`G.adj <networkx.Graph.adj>`,
{meth}`G.successors <networkx.DiGraph.successors>`,
{meth}`G.predecessors <networkx.DiGraph.predecessors>`) is the order of
edge addition. However, the order of G.edges is the order of the adjacencies
which includes both the order of the nodes and each
node's adjacencies. See example below:
```

```{code-cell}
DG = nx.DiGraph()
DG.add_edge(2, 1)   # adds the nodes in order 2, 1
DG.add_edge(1, 3)
DG.add_edge(2, 4)
DG.add_edge(1, 2)
assert list(DG.successors(2)) == [1, 4]
assert list(DG.edges) == [(2, 1), (2, 4), (1, 3), (1, 2)]
```

## Examining elements of a graph

We can examine the nodes and edges. Four basic graph properties facilitate
reporting: `G.nodes`, `G.edges`, `G.adj` and `G.degree`. These
are set-like views of the nodes, edges, neighbors (adjacencies), and degrees
of nodes in a graph. They offer a continually updated read-only view into
the graph structure. They are also dict-like in that you can look up node
and edge data attributes via the views and iterate with data attributes
using methods `.items()`, `.data()`.
If you want a specific container type instead of a view, you can specify one.
Here we use lists, though sets, dicts, tuples and other containers may be
better in other contexts.

```{code-cell}
list(G.nodes)
```

```{code-cell}
list(G.edges)
```

```{code-cell}
list(G.adj[1])  # or list(G.neighbors(1))
```

```{code-cell}
G.degree[1]  # the number of edges incident to 1
```

One can specify to report the edges and degree from a subset of all nodes
using an {term}`nbunch`. An _nbunch_ is any of: `None` (meaning all nodes),
a node, or an iterable container of nodes that is not itself a node in the
graph.

```{code-cell}
G.edges([2, 'm'])
```

```{code-cell}
G.degree([2, 3])
```

### Access patterns

Both nodes and edges can be accessed either as attributes, e.g. `G.nodes` or
`G.edges`, or as callables e.g. `G.nodes()` or `G.edges()`.
The attribute-like access pattern is most convenient when setting/modifying node or
edge data:

```{code-cell}
G.nodes["spam"]["color"] = "blue"
G.edges[(1, 2)]["weight"] = 10
```

While the callable pattern is useful for inspecting node or edge attributes
(and edge keys for multigraphs):

```{code-cell}
G.edges(data=True)
```

```{code-cell}
G.nodes(data="color")
```

See the [section on attributes](attributes) for details.

## Removing elements from a graph

One can remove nodes and edges from the graph in a similar fashion to adding.
Use methods
{meth}`Graph.remove_node`,
{meth}`Graph.remove_nodes_from`,
{meth}`Graph.remove_edge`
and
{meth}`Graph.remove_edges_from`.

Removing a node also removes its incident edges:

```{code-cell}
G.remove_node(2)
G.remove_nodes_from("spam")
```

```{code-cell}
list(G.nodes)
```

```{code-cell}
list(G.edges)
```

Removing a specific edge only affects that edge:

```{code-cell}
G.remove_edge(1, 3)
```

```{code-cell}
list(G.nodes)
```

```{code-cell}
list(G.edges)
```

## Using the graph constructors

Graph objects do not have to be built up incrementally - data specifying
graph structure can be passed directly to the constructors of the various
graph classes.
When creating a graph structure by instantiating one of the graph
classes you can specify data in several formats.

```{code-cell}
G.add_edge(1, 2)
H = nx.DiGraph(G)  # create a DiGraph using the connections from G
list(H.edges())
```

```{code-cell}
edgelist = [(0, 1), (1, 2), (2, 3)]
H = nx.Graph(edgelist)  # create a graph from an edge list
list(H.edges())
```

```{code-cell}
adjacency_dict = {0: (1, 2), 1: (0, 2), 2: (0, 1)}
H = nx.Graph(adjacency_dict)  # create a Graph dict mapping nodes to nbrs
list(H.edges())
```

## What to use as nodes and edges

You might notice that nodes and edges are not specified as NetworkX
objects. This leaves you free to use meaningful items as nodes and
edges. The most common choices are numbers or strings, but a node can
be any hashable object (except `None`), and an edge can be associated
with any object `x` using `G.add_edge(n1, n2, object=x)`.

As an example, `n1` and `n2` could be protein objects from the RCSB Protein
Data Bank, and `x` could refer to an XML record of publications detailing
experimental observations of their interaction.

We have found this power quite useful, but its abuse
can lead to surprising behavior unless one is familiar with Python.
If in doubt, consider using {func}`~relabel.convert_node_labels_to_integers` to obtain
a more traditional graph with integer labels.

## Accessing edges and neighbors

In addition to the views {attr}`Graph.edges`, and {attr}`Graph.adj`,
access to edges and neighbors is possible using subscript notation.

```{code-cell}
G = nx.Graph([(1, 2, {"color": "yellow"})])
G[1]  # same as G.adj[1]
```

```{code-cell}
G[1][2]
```

```{code-cell}
G.edges[1, 2]
```

You can get/set the attributes of an edge using subscript notation
if the edge already exists.

```{code-cell}
G.add_edge(1, 3)
G[1][3]['color'] = "blue"
G.edges[1, 2]['color'] = "red"
G.edges[1, 2]
```

Fast examination of all (node, adjacency) pairs is achieved using
`G.adjacency()`, or `G.adj.items()`.
Note that for undirected graphs, adjacency iteration sees each edge twice.

```{code-cell}
FG = nx.Graph()
FG.add_weighted_edges_from([(1, 2, 0.125), (1, 3, 0.75), (2, 4, 1.2), (3, 4, 0.375)])
for n, nbrs in FG.adj.items():
   for nbr, eattr in nbrs.items():
       wt = eattr['weight']
       if wt < 0.5: print(f"({n}, {nbr}, {wt:.3})")
```

Convenient access to all edges is achieved with the edges property.

```{code-cell}
for (u, v, wt) in FG.edges.data('weight'):
    if wt < 0.5:
        print(f"({u}, {v}, {wt:.3})")
```

(attributes)=

## Adding attributes to graphs, nodes, and edges

Attributes such as weights, labels, colors, or whatever Python object you like,
can be attached to graphs, nodes, or edges.

Each graph, node, and edge can hold key/value attribute pairs in an associated
attribute dictionary (the keys must be hashable). By default these are empty,
but attributes can be added or changed using `add_edge`, `add_node` or direct
manipulation of the attribute dictionaries named `G.graph`, `G.nodes`, and
`G.edges` for a graph `G`.

### Graph attributes

Assign graph attributes when creating a new graph

```{code-cell}
G = nx.Graph(day="Friday")
G.graph
```

Or you can modify attributes later

```{code-cell}
G.graph['day'] = "Monday"
G.graph
```

### Node attributes

Add node attributes using `add_node()`, `add_nodes_from()`, or `G.nodes`

```{code-cell}
G.add_node(1, time='5pm')
G.add_nodes_from([3], time='2pm')
G.nodes[1]
```

```{code-cell}
G.nodes[1]['room'] = 714
G.nodes.data()
```

Note that adding a node to `G.nodes` does not add it to the graph, use
`G.add_node()` to add new nodes. Similarly for edges.

### Edge Attributes

Add/change edge attributes using `add_edge()`, `add_edges_from()`,
or subscript notation.

```{code-cell}
G.add_edge(1, 2, weight=4.7 )
G.add_edges_from([(3, 4), (4, 5)], color='red')
G.add_edges_from([(1, 2, {'color': 'blue'}), (2, 3, {'weight': 8})])
G[1][2]['weight'] = 4.7
G.edges[3, 4]['weight'] = 4.2
```

The special attribute `weight` should be numeric as it is used by
algorithms requiring weighted edges.

## Directed graphs

The {class}`DiGraph` class provides additional methods and properties specific
to directed edges, e.g.,
{attr}`DiGraph.out_edges`, {attr}`DiGraph.in_degree`,
{meth}`DiGraph.predecessors`, {meth}`DiGraph.successors` etc.
To allow algorithms to work with both classes easily, the directed versions of
{meth}`neighbors <DiGraph.neighbors>` is equivalent to
{meth}`successors <DiGraph.successors>` while {attr}`DiGraph.degree` reports the sum
of {attr}`DiGraph.in_degree` and {attr}`DiGraph.out_degree` even though that may
feel inconsistent at times.

```{code-cell}
DG = nx.DiGraph()
DG.add_weighted_edges_from([(1, 2, 0.5), (3, 1, 0.75)])
DG.out_degree(1, weight='weight')
```

```{code-cell}
DG.degree(1, weight='weight')
```

```{code-cell}
list(DG.successors(1))
```

```{code-cell}
list(DG.neighbors(1))
```

Some algorithms work only for directed graphs and others are not well
defined for directed graphs. Indeed the tendency to lump directed
and undirected graphs together is dangerous. If you want to treat
a directed graph as undirected for some measurement you should probably
convert it using {meth}`Graph.to_undirected` or with

```{code-cell}
H = nx.Graph(G)  # create an undirected graph H from a directed graph G
```

## Multigraphs

NetworkX provides classes for graphs which allow multiple edges
between any pair of nodes. The {class}`MultiGraph` and
{class}`MultiDiGraph`
classes allow you to add the same edge twice, possibly with different
edge data. This can be powerful for some applications, but many
algorithms are not well defined on such graphs.
Where results are well defined,
e.g., {meth}`MultiGraph.degree` we provide the function. Otherwise you
should convert to a standard graph in a way that makes the measurement
well defined.

```{code-cell}
MG = nx.MultiGraph()
MG.add_weighted_edges_from([(1, 2, 0.5), (1, 2, 0.75), (2, 3, 0.5)])
dict(MG.degree(weight='weight'))
```

```{code-cell}
GG = nx.Graph()
for n, nbrs in MG.adjacency():
   for nbr, edict in nbrs.items():
       minvalue = min([d['weight'] for d in edict.values()])
       GG.add_edge(n, nbr, weight = minvalue)

nx.shortest_path(GG, 1, 3)
```

## Graph generators and graph operations

In addition to constructing graphs node-by-node or edge-by-edge, they
can also be generated by

### 1. Applying classic graph operations, such as:

```{eval-rst}
.. autosummary::

    ~classes.function.subgraph
    ~algorithms.operators.binary.union
    ~algorithms.operators.binary.disjoint_union
    ~algorithms.operators.product.cartesian_product
    ~algorithms.operators.binary.compose
    ~algorithms.operators.unary.complement
    ~classes.function.create_empty_copy
    ~classes.function.to_undirected
    ~classes.function.to_directed
```

### 2. Using a call to one of the classic small graphs, e.g.,

```{eval-rst}
.. autosummary::

    ~generators.small.petersen_graph
    ~generators.small.tutte_graph
    ~generators.small.sedgewick_maze_graph
    ~generators.small.tetrahedral_graph
```

### 3. Using a (constructive) generator for a classic graph, e.g.,

```{eval-rst}
.. autosummary::

    ~generators.classic.complete_graph
    ~algorithms.bipartite.generators.complete_bipartite_graph
    ~generators.classic.barbell_graph
    ~generators.classic.lollipop_graph
```

like so:

```{code-cell}
K_5 = nx.complete_graph(5)
K_3_5 = nx.complete_bipartite_graph(3, 5)
barbell = nx.barbell_graph(10, 10)
lollipop = nx.lollipop_graph(10, 20)
```

### 4. Using a stochastic graph generator, e.g,

```{eval-rst}
.. autosummary::

    ~generators.random_graphs.erdos_renyi_graph
    ~generators.random_graphs.watts_strogatz_graph
    ~generators.random_graphs.barabasi_albert_graph
    ~generators.random_graphs.random_lobster
```

like so:

```{code-cell}
er = nx.erdos_renyi_graph(100, 0.15)
ws = nx.watts_strogatz_graph(30, 3, 0.1)
ba = nx.barabasi_albert_graph(100, 5)
red = nx.random_lobster(100, 0.9, 0.9)
```

### 5. Reading a graph stored in a file using common graph formats

NetworkX supports many popular formats, such as edge lists, adjacency lists,
GML, GraphML, LEDA and others.

```{code-cell}
nx.write_gml(red, "path.to.file")
mygraph = nx.read_gml("path.to.file")
```

For details on graph formats see {doc}`/reference/readwrite/index`
and for graph generator functions see {doc}`/reference/generators`

## Analyzing graphs

The structure of `G` can be analyzed using various graph-theoretic
functions such as:

```{code-cell}
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3)])
G.add_node("spam")       # adds node "spam"
list(nx.connected_components(G))
```

```{code-cell}
sorted(d for n, d in G.degree())
```

```{code-cell}
nx.clustering(G)
```

Some functions with large output iterate over (node, value) 2-tuples.
These are easily stored in a `dict` structure if you desire.

```{code-cell}
sp = dict(nx.all_pairs_shortest_path(G))
sp[3]
```

See {doc}`/reference/algorithms/index` for details on graph algorithms
supported.

## Floating point considerations

Many NetworkX algorithms work with numeric values, such as edge weights. Once
your input contains floating point numbers,
**all results are inherently approximate** due to the limited precision of
floating point arithmetic. This is especially true for algorithms such as
shortest-path, flows, cuts, minimum-spanning, etc. Basically any time a min or
max value is computed.

For example:

```{code-cell}
import networkx as nx

eps = 1e-17

G = nx.DiGraph()
G.add_edge('A', 'B', weight=0.1)
G.add_edge('B', 'C', weight=0.1)
G.add_edge('C', 'D', weight=0.1)
G.add_edge('A', 'D', weight=0.3 + eps)

path = nx.shortest_path(G, 'A', 'D', weight='weight')
print(path)
```

Even though `A -> B -> C -> D` has a total weight of `0.3`, the direct edge
`A -> D` with `0.3 + 1e-17` is selected. This demonstrates that algorithms
treat floating point numbers as exact, so very small differences can change the
outcome.

Floating point arithmetic can produce unintuitive results because certain
values, such as `0.3`, cannot be represented exactly in binary. For example:

```{code-cell}
0.1 + 0.1 + 0.1 > 0.3
```

In general, when using floating point numbers in NetworkX, you should expect
results to be approximate rather than exact. Multiplying weights by a large
number and converting them to integers can help reduce some subtle comparison
issues, but it does not fully eliminate them. NetworkX does not automatically
apply tolerances in numeric comparisons.

(using-networkx-backends)=

## Using NetworkX backends

NetworkX can be configured to use separate thrid-party backends to improve
performance and add functionality. Backends are optional, installed separately,
and can be enabled either directly in the user's code or through environment
variables.

Several backends are available to accelerate NetworkX--often
significantly--using GPUs, parallel processing, and other optimizations, while
other backends add additional features such as graph database
integration. Multiple backends can be used together to compose a NetworkX
runtime environment optimized for a particular system or use case.

```{note}
Refer to the {doc}`/backends` section to see a list of available backends known
to work with the current stable release of NetworkX.
```

NetworkX uses backends by **_dispatching_** function calls at runtime to
corresponding functions provided by backends, either **automatically** via
configuration variables, or **explicitly** by hard-coded arguments to functions.

### Automatic dispatch

Automatic dispatch is possibly the easiest and least intrusive means by which a
user can use backends with NetworkX code. This technique is useful for users
that want to write portable code that runs on systems without specific
backends, or simply want to use backends for existing code without
modifications.

The example below configures NetworkX to automatically dispatch to a backend
named `fast_backend` for all NetworkX functions that `fast_backend` supports.

- If `fast_backend` does not support a NetworkX function used by the
  application, the default NetworkX implementation for that function will be
  used.

- If `fast_backend` is not installed on the system running this code, an
  exception will be raised.

```{code-block}
bash$> NETWORKX_BACKEND_PRIORITY=fast_backend python my_script.py
```

```{code-block}
:caption: my_script.py
import networkx as nx
G = nx.karate_club_graph()
pr = nx.pagerank(G)  # runs using backend from NETWORKX_BACKEND_PRIORITY, if set
```

The equivalent configuration can be applied to NetworkX directly to the code
through the NetworkX `config` global parameters, which may be useful if
environment variables are not suitable. This will override the corresponding
environment variable allowing backends to be enabled programmatically in Python
code. However, the tradeoff is slightly less portability as updating the
backend specification may require a small code change instead of simply
updating an environment variable.

```{code-cell}
:tags: [skip-execution]
nx.config.backend_priority = ["fast_backend"]
pr = nx.pagerank(G)
```

Automatic dispatch using the `NETWORKX_BACKEND_PRIORITY` environment variable
or the `nx.config.backend_priority` global config also allows for the
specification of multiple backends, ordered based on the priority which
NetworkX should attempt to dispatch to.

The following examples both configure NetworkX to dispatch functions first to
`fast_backend` if it supports the function, then `other_backend` if
`fast_backend` does not, then finally the default NetworkX implementation if no
backend specified can handle the call.

```{code-block}
bash$> NETWORKX_BACKEND_PRIORITY="fast_backend,other_backend" python my_script.py
```

```{code-cell}
:tags: [skip-execution]
nx.config.backend_priority = ["fast_backend", "other_backend"]
```

````{tip}
NetworkX includes debug logging calls using Python's standard logging
mechanism.  These can be enabled to help users understand when and how backends
are being used.

To enable debug logging only in NetworkX modules:
   ```{code-block}
   import logging
   _l = logging.getLogger("networkx")
   _l.addHandler(_h:=logging.StreamHandler())
   _h.setFormatter(logging.Formatter("%(levelname)s:NetworkX:%(message)s"))
   _l.setLevel(logging.DEBUG)
   ```
or to enable it globally:
   ```{code-block}
   logging.basicConfig(level=logging.DEBUG)
   ```
````

### Explicit dispatch

Backends can also be used explicitly on a per-function call basis by specifying
a backend using the `backend=` keyword argument. This technique not only
requires that the backend is installed, but _also_ requires that the backend
implement the function, since NetworkX will not fall back to the default NetworkX
implementation if a backend is specified with `backend=`.

This is possibly the least portable option, but has the advantage that NetworkX
will raise an exception if `fast_backend` cannot be used, which is useful for
users that require a specific implementation. Explicit dispatch can also
provide a more interactive experience and is especially useful for
demonstrations, experimentation, and debugging.

```{code-cell}
:tags: [skip-execution]
pr = nx.pagerank(G, backend="fast_backend")
```

### Advanced dispatching options

The NetworkX dispatcher allows users to use backends for NetworkX code in very
specific ways not covered in this tutorial. Refer to the
{doc}`/reference/backends` reference section for details on topics such as:

- Control of how specific function types (algorithms vs. generators) are
  dispatched to specific backends
- Details on automatic conversions to/from backend and NetworkX graphs for
  dispatch and fallback
- Caching graph conversions
- Explicit backend graph instantiation and dispatching based on backend graph
  types
- and more...

## Drawing graphs

NetworkX is not primarily a graph drawing package but basic drawing with
Matplotlib as well as an interface to use the open source Graphviz software
package are included. These are part of the {doc}`networkx.drawing <reference/drawing>`
module and will be imported if possible.

First import Matplotlib's plot interface (pylab works too)

```{code-cell}
import matplotlib.pyplot as plt
```

To test if the import of `~networkx.drawing.nx_pylab` was successful draw `G`
using one of

```{code-cell}
G = nx.petersen_graph()
subax1 = plt.subplot(121)
nx.draw(G, with_labels=True, font_weight='bold')
subax2 = plt.subplot(122)
nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
```

when drawing to an interactive display. Note that you may need to issue a
Matplotlib

```python
plt.show()
```

command if you are not using matplotlib in interactive mode.

```{code-cell}
options = {
    'node_color': 'black',
    'node_size': 100,
    'width': 3,
}
subax1 = plt.subplot(221)
nx.draw_random(G, **options)
subax2 = plt.subplot(222)
nx.draw_circular(G, **options)
subax3 = plt.subplot(223)
nx.draw_spectral(G, **options)
subax4 = plt.subplot(224)
nx.draw_shell(G, nlist=[range(5,10), range(5)], **options)
```

You can find additional options via {func}`~drawing.nx_pylab.draw_networkx` and
layouts via the {mod}`layout module<networkx.drawing.layout>`.
You can use multiple shells with {func}`~drawing.nx_pylab.draw_shell`.

```{code-cell}
G = nx.dodecahedral_graph()
shells = [[2, 3, 4, 5, 6], [8, 1, 0, 19, 18, 17, 16, 15, 14, 7], [9, 10, 11, 12, 13]]
nx.draw_shell(G, nlist=shells, **options)
```

To save drawings to a file, use, for example

```pycon
>>> nx.draw(G)
>>> plt.savefig("path.png")
```

This function writes to the file `path.png` in the local directory. If Graphviz and
PyGraphviz or pydot, are available on your system, you can also use
`networkx.drawing.nx_agraph.graphviz_layout` or
`networkx.drawing.nx_pydot.graphviz_layout` to get the node positions, or write
the graph in dot format for further processing.

```pycon
>>> from networkx.drawing.nx_pydot import write_dot
>>> pos = nx.nx_agraph.graphviz_layout(G)
>>> nx.draw(G, pos=pos)
>>> write_dot(G, 'file.dot')
```

See {doc}`/reference/drawing` for additional details.

## NX-Guides

If you are interested in learning more about NetworkX, graph theory and network analysis
then you should check out {doc}`nx-guides <nx-guides:index>`. There you can find tutorials,
real-world applications and in-depth examinations of graphs and network algorithms.
All the material is official and was developed and curated by the NetworkX community.
