"""Time dependent algorithms."""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["cd_index"]

@not_implemented_for("undirected")
@not_implemented_for("multigraph")
def cd_index(G, node, time_delta = None):
   """Compute the CD index.

   Calculates the CD index for the graph based on the given "focal patent" node.

   Parameters
   ----------
   G : graph
      A directed networkx graph.
   node : focal node that represents the focal patent
      Compute triangles for nodes in this container.

   Returns
   -------
   cd : float
      The CD index calculated for the G graph.

   Examples
   --------

   Notes
   -----
   

   """

   suc, pred = list(G.successors(node)), list(G.predecessors(node))

   if not suc:
      raise ValueError("This node has no successors.")
   
   if time_delta is not None:
      for i in pred:
         if G.nodes[i]['time'] > time_delta:
            pred.remove(i)

   if not pred:
      raise ValueError("This node has no predecessors.")

   b = [int(any((i, j) in G.edges() for j in suc)) for i in pred]

   n = set(pred)
   for s in suc:
      n |= set(G.predecessors(s)) - {node}

   return round(sum((-2) * bi + 1 for bi in b) / len(n), 2)
