import networkx as nx
from collections import defaultdict
from itertools import combinations
from operator import itemgetter

# Define the default maximum flow function.
from networkx.algorithms.flow import edmonds_karp
from networkx.utils import not_implemented_for

default_flow_func = edmonds_karp

__all__ = ["unweighted_k_components", "k_components"]

@not_implemented_for("undirected")
@nx._dispatch
def unweighted_k_components(G, flow_func=None):
    # Implementation for computing unweighted k-components
    k_components = defaultdict(list)
    if flow_func is None:
        flow_func = default_flow_func

    for component in nx.strongly_connected_components(G):
        comp = set(component)
        if len(comp) > 1:
            k_components[1].append(comp)

    bicomponents = [G.subgraph(c) for c in nx.strongly_connected_components(G)]
    for bicomponent in bicomponents:
        bicomp = set(bicomponent)
        if len(bicomp) > 2:
            k_components[2].append(bicomp)

    for B in bicomponents:
        if len(B) <= 2:
            continue
        k = nx.node_connectivity(B, flow_func=flow_func)
        if k > 2:
            k_components[k].append(set(B))

        cuts = list(all_node_cuts_directed(B, k=k, flow_func=flow_func))
        stack = [(k, _generate_partition_directed(B, cuts, k))]
        while stack:
            (parent_k, partition) = stack[-1]
            try:
                nodes = next(partition)
                C = B.subgraph(nodes)
                this_k = nx.node_connectivity(C, flow_func=flow_func)
                if this_k > parent_k and this_k > 2:
                    k_components[this_k].append(set(C))
                cuts = list(all_node_cuts_directed(C, k=this_k, flow_func=flow_func))
                if cuts:
                    stack.append((this_k, _generate_partition_directed(C, cuts, this_k)))
            except StopIteration:
                stack.pop()

    return _reconstruct_k_components(k_components)

def k_components(G, weight=None, flow_func=None):
    # Implementation for computing weighted k-components
    # Compute the weighted k-components of a directed graph G.
    # k-components are subsets of nodes such that removing them from the graph increases its connectivity.
    # This implementation is based on the concept of node connectivity and uses Edmonds-Karp algorithm for flow computation.
    if weight is None:
        return unweighted_k_components(G, flow_func=flow_func)

    # TODO: Implement weighted k-components functionality
    pass

def _consolidate(sets, k):
    G = nx.DiGraph()
    nodes = dict(enumerate(sets))
    G.add_nodes_from(nodes)
    G.add_edges_from(
        (u, v) for u, v in combinations(nodes, 2) if len(nodes[u] & nodes[v]) >= k
    )
    for component in nx.strongly_connected_components(G):
        yield set.union(*[nodes[n] for n in component])

def _generate_partition_directed(G, cuts, k):
    def has_nbrs_in_partition(G, node, partition):
        return any(n in partition for n in G.predecessors(node)) or any(n in partition for n in G.successors(node))

    components = []
    nodes = {n for n, d in G.in_degree() if d > k} | {n for n, d in G.out_degree() if d > k}
    H = G.subgraph(nodes)
    for cc in nx.strongly_connected_components(H):
        component = set(cc)
        for cut in cuts:
            for node in cut:
                if has_nbrs_in_partition(G, node, cc):
                    component.add(node)
        if len(component) < G.order():
            components.append(component)
    yield from _consolidate(components, k + 1)

def all_node_cuts_directed(G, k, flow_func=None):
    if flow_func is None:
        flow_func = default_flow_func

    for source, target in combinations(G, 2):
        if nx.node_connectivity(G, s=source, t=target, flow_func=flow_func) >= k:
            yield {source, target}

def _reconstruct_k_components(k_comps):
    result = {}
    max_k = max(k_comps)
    for k in reversed(range(1, max_k + 1)):
        if k == max_k:
            result[k] = list(_consolidate(k_comps[k], k))
        elif k not in k_comps:
            result[k] = list(_consolidate(result[k + 1], k))
        else:
            nodes_at_k = set.union(*k_comps[k])
            to_add = [c for c in result[k + 1] if any(n not in nodes_at_k for n in c)]
            if to_add:
                result[k] = list(_consolidate(k_comps[k] + to_add, k))
            else:
                result[k] = list(_consolidate(k_comps[k], k))
    return result

def build_k_number_dict(kcomps):
    result = {}
    for k, comps in sorted(kcomps.items(), key=itemgetter(0)):
        for comp in comps:
            for node in comp:
                result[node] = k
    return result
        
