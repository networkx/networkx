import networkx as nx
import math

class UCIGraph(nx.DiGraph):

    def get_tree_children(self, nodes: list)->list:
        '''Gets the children(successors) of each node

        Parameters
        ----------
        nodes: list of nodes

        Returns
        ----------
        list of children(successors)
        '''
        assert nx.is_tree(self), "Graph is not a tree"
        children: list = []
        for node in nodes:
            for k in self.successors(node):
                children.append(k)
        return children

    def num_independent_sets(self):
        '''
        Returns
        ----------
        total number of independent sets.
        '''
        postorder_nodes = nx.dfs_postorder_nodes(self)
        num_ind_sets_at_node = dict()

        for node in postorder_nodes:
            children = self.get_tree_children([node])  # get children of the node
            grandchildren = self.get_tree_children(children)  # get grandchildren of the node
            
            if len(children) == 0 and len(grandchildren) == 0:
                # a single node has 2 ind sets. {empty, self}
                num_ind_sets_at_node[node] = 2
            elif len(grandchildren) == 0:
                # if grandchildren are empty but children are not,
                # number of ind sets should be product of children + self.
                num_ind_sets_at_node[node] = math.prod([num_ind_sets_at_node[c] for c in children])+1
            else:
                # if both children and grandchildren are not empty,
                # number of ind sets is should be the products children(excluding the current node) and product of grandchildren
                num_ind_sets_at_node[node] =  math.prod([num_ind_sets_at_node[c] for c in children]) +\
                    math.prod([num_ind_sets_at_node[gc] for gc in grandchildren])
        return num_ind_sets_at_node[node] #node will always be the root

