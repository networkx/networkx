import networkx as nx
cimport cython

@cython.cdivision(True)
cpdef object generate_diGraph(object G, list m, int priority, bint flag):
    cdef object ans = nx.DiGraph()
    # info
    cdef dict priority_info = nx.get_node_attributes(G, "priority")
    cdef dict Gruop_info = nx.get_node_attributes(G, "Group")
    cdef dict matching_info = nx.get_node_attributes(G, "isMatched")

    # generate graph for augmenting_path_v1
    if flag is True:
        # add new nodes 's' and 't' and add edges to the relevant nodes in V1
        ans.add_node('s')
        ans.add_node('t')
        for node in G.nodes:
            ans.add_node(node)
            if Gruop_info[node] == 1 and matching_info[node] is False and priority_info[node] == priority:
                ans.add_edges_from([('s',node)])
            if Gruop_info[node] == 1 and matching_info[node] is True and priority_info[node] > priority:
                ans.add_edges_from([(node,'t')])

        # add the edges from G with the right direction
        for edge in G.edges:
            if Gruop_info[edge[0]] == 1 and Gruop_info[edge[1]] == 2:
                u = edge[0]
                v = edge[1]

                if (u,v) in m:
                    ans.add_edges_from([(v, u)])
                elif (v,u) in m:
                    ans.add_edges_from([(v, u)])
                # {u,v} is not a matching edge
                else:
                    ans.add_edges_from([(u, v)])

            else:
                v = edge[0]
                u = edge[1]

                if (u, v) in m:
                    ans.add_edges_from([(v, u)])
                elif (v, u) in m:
                    ans.add_edges_from([(v, u)])
                    # {u,v} is not a matching edge
                else:
                    ans.add_edges_from([(u, v)])

        return ans

    # flag is false , generate graph for augmenting_path_v2
    else:
        # add new nodes 's' and 't' and add edges to the relevant nodes in V2
        ans.add_node('s')
        ans.add_node('t')
        for node in G.nodes:
            ans.add_node(node)
            if Gruop_info[node] == 2 and matching_info[node] is True and priority_info[node] > priority:
                ans.add_edges_from([('s', node)])
            if Gruop_info[node] == 2 and matching_info[node] is False and priority_info[node] == priority:
                ans.add_edges_from([(node, 't')])
        # add the edges from G with the right direction
        for edge in G.edges:
            if Gruop_info[edge[0]] == 1 and Gruop_info[edge[1]] == 2:
                u = edge[0]
                v = edge[1]

                if (u,v) in m:
                    ans.add_edges_from([(v,u)])
                elif (v,u) in m:
                    ans.add_edges_from([(v, u)])
                else:
                    ans.add_edges_from([(u,v)])

            else:
                v = edge[0]
                u = edge[1]

                if (u,v) in m:
                    ans.add_edges_from([(v,u)])
                elif (v,u) in m:
                    ans.add_edges_from([(v, u)])
                else:
                    ans.add_edges_from([(u,v)])

        return ans
