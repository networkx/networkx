

import copy
import numpy as np
import networkx as nx
from  networkx.utils import contains_only


class WeightedPartition(object):
    """Represent a weighted Graph Partition

       The main object keeping track of the nodes in each partition is the
       communities attribute.
    """
    def __init__(self, graph, communities=None):
        """ initialize partition of graph, with optional communities

        Parameters
        ----------
        graph : networkx graph
        communities : list of sets, optional
            a list of sets with nodes in each set
            if communities is None, will initialize with
            one  per node

        Returns
        -------
        part : WeightedPartition object
        """
        # assert graph has edge weights, and no negative weights
        mat = nx.adjacency_matrix(graph).toarray() #from sparse to dense
        if mat.min() < 0:
            raise ValueError('Graph has invalid negative weights')
        ## adjacency_matrix.todense() doubles the diagonal
        diagind = np.diag_indices_from(mat)
        mat[diagind] /= 2.
        self.graph = nx.from_numpy_matrix(mat)
        if communities is None:
            self._communities = self._init_communities_from_nodes()
        else:
            self.set_communities(communities)
        self.total_edge_weight = graph.size(weight='weight')
        self.degrees = graph.degree(weight='weight')

    @property
    def communities(self):
        """list of sets decribing the communities"""
        return self._communities

    @communities.setter
    def communities(self, value):
        self.set_communities(value)

    def _init_communities_from_nodes(self):
        """ creates a new communities with one node per community
        eg nodes = [0,1,2] -> communities = [set([0]), set([1]), set([2])]
        """
        return [set([node]) for node in self.graph.nodes()]


    def communities_degree(self):
        """ calculates the joint degree of a community"""
        communities_degrees = []
        for com in self.communities:
            tmp = np.sum([self.graph.degree(weight='weight')[x] for x in com])
            communities_degrees.append(tmp)
        return communities_degrees

    def get_node_community(self, node):
        """returns the node's community"""
        try:
            return [val for val,x in enumerate(self.communities) if node in x][0]
        except IndexError:
            if not node in self.graph.nodes():
                raise ValueError('node:{0} is not in the graph'.format(node))
            else:
                raise StandardError('cannot find community for node '\
                    '{0}'.format(node))

    def set_communities(self, communities):
        """ set the partition communities to the input communities"""
        if self._allnodes_in_communities(communities):
            self._communities = communities
        else:
            raise ValueError('missing nodes {0}'.format(communities))


    def _allnodes_in_communities(self, communities):
        """ checks all nodes are represented in communities, also catches
        duplicate nodes"""
        if not (isinstance(communities, list) and \
            contains_only(communities, set)):
            raise TypeError('communities should ba a list of sets')
        ## simple count to check for all nodes
        return len(self.graph.nodes()) == \
            len([item for com in communities for item in com])

    def node_degree(self, node):
        """ find the summed weight of all node edges
        """
        return self.graph.degree(weight='weight')[node]


    def node_degree_by_community(self, node):
        """ Find the number of links from a node to each community
        Returns
        -------
        comm_weights : list
            list holding the weighted degree of a node to each community
        """
        comm_weights = [0] * len(self.communities)
        for neighbor, data in self.graph[node].items():
            if neighbor == node:
                continue
            tmpcomm = self.get_node_community(neighbor)
            comm_weights[tmpcomm] += data.get('weight', 1)
        return comm_weights


    def degree_by_community(self):
        """ sum of all edges within or between communities
        for each community
        Returns
        -------
        weights : list
            list is size of total number of communities"""
        comm = self.communities
        weights = [0] * len(comm)
        all_degree_weights = self.graph.degree(weight='weight')
        for node, weight in all_degree_weights.items():
            node_comm = self.get_node_community(node)
            weights[node_comm] += weight
        return weights

    def degree_within_community(self):
        """ sum of weighted edges strictly inside each community
        including self loops"""
        comm = self.communities
        weights = [0] * len(comm)
        comm = self.communities
        for val, nodeset in enumerate(comm):
            for node in nodeset:
                nodes_within = set([x for x in self.graph[node].keys() \
                    if x in nodeset])
                if len(nodes_within) < 1:
                    continue
                if node in nodes_within:
                    weights[val] += self.graph[node][node]['weight']
                    nodes_within.remove(node)
                weights[val] += np.sum(self.graph[node][x]['weight']/ 2. \
                    for x in nodes_within)
        return weights


    def modularity(self):
        """Calculates the proportion of within community edges compared to
        between community edges for all nodes in graph with given partition

        Parameters
        ----------
        partition : weighted graph partition object

        Returns
        -------
        modularity : float
            value reflecting the relation of within community connection
            to across community connections


        References
        ----------
        .. [1] M. Newman, "Fast algorithm for detecting community structure
            in networks", Physical Review E vol. 69(6), 2004.

        """
        if self.graph.is_directed():
            raise TypeError('only valid on non directed graphs')

        m2 = self.total_edge_weight
        internal_connect = np.array(self.degree_within_community())
        total = np.array(self.degree_by_community())
        return np.sum(internal_connect/m2 - (total/(2*m2))**2)



class LouvainCommunityDetection(object):
    """ Uses the Louvain Community Detection algorithm to detect
    communities in networks

    Parameters
    ----------
    graph : netwrokx Graph object
    communities : list of sets, optional
        initial identified communties
    minthr : float, optional
        minimum threshold value for change in modularity
        default(0.0000001)

    Methods
    -------
    run()
        run the algorithm to find partitions at multiple levels

    Examples
    --------
    >>> louvain = LouvainCommunityDetection(graph) # doctests: +SKIP
    >>> partitions = louvain.run() # doctests: +SKIP
    >>> ## best partition # doctests: +SKIP
    >>> bestpart = partitions[-1] # doctests: +SKIP
    >>> bestpart.modularity() # doctests: +SKIP

    References
    ----------
    .. [1] VD Blondel, JL Guillaume, R Lambiotte, E Lefebvre, "Fast
        unfolding of communities in large networks", Journal of Statistical
        Mechanics: Theory and Experiment vol.10, P10008  2008.

    """

    def __init__(self, graph, communities=None, minthr=0.0000001):
        """initialize the algorithm with a graph and (optional) initial
        community partition , use minthr to provide a stopping limit
        for the algorith (based on change in modularity)"""
        self.graph = graph
        self.initial_communities = communities
        self.minthr = minthr

    def run(self):
        """ run the algorithm to find partitions in graph

        Returns
        -------
        partitions : list
        a list containing instances of a WeightedPartition with the
        community partition reflecting that level of the algorithm
        The last item in the list is the final partition
        The first item was the initial partition
        """
        dendogram = self._gen_dendogram()
        partitions = self._partitions_from_dendogram(dendogram)
        return [WeightedPartition(self.graph, part) for part in partitions]


    def _gen_dendogram(self):
        """generate dendogram based on muti-levels of partitioning
        """
        if type(self.graph) != nx.Graph :
            raise TypeError("Bad graph type, use only non directed graph")

        #special case, when there is no link
        #the best partition is everyone in its communities
        if self.graph.number_of_edges() == 0 :
            raise IOError('graph has no edges why do you want to partition?')

        current_graph = self.graph.copy()
        part = WeightedPartition(self.graph, self.initial_communities)
        # first pass
        mod = part.modularity()
        dendogram = list()
        new_part = self._one_level(part, self.minthr)
        new_mod = new_part.modularity()

        dendogram.append(new_part)
        mod = new_mod
        current_graph, _ = meta_graph(new_part)

        while True :
            partition = WeightedPartition(current_graph)
            newpart = self._one_level(partition, self.minthr)
            new_mod = newpart.modularity()
            if new_mod - mod < self.minthr :
                break

            dendogram.append(newpart)
            mod = new_mod
            current_graph,_ = meta_graph(newpart)
        return dendogram

    def _one_level(self, part, min_modularity= .0000001):
        """run one level of partitioning"""
        curr_mod = part.modularity()
        modified = True
        while modified:
            modified = False
            all_nodes = [x for x in part.graph.nodes()]
            np.random.shuffle(all_nodes)
            for node in all_nodes:
                node_comm = part.get_node_community(node)
                delta_mod = self._calc_delta_modularity(node, part)
                #print node, delta_mod
                if delta_mod.max() <= 0.0:
                    # no increase by moving this node
                    continue
                best_comm = delta_mod.argmax()
                if not best_comm == node_comm:
                    new_part = self._move_node(part, node, best_comm)
                    part = new_part
                    modified = True
            new_mod = part.modularity()
            change_in_modularity = new_mod - curr_mod
            if change_in_modularity < min_modularity:
                return part
        return part

    def _calc_delta_modularity(self, node, part):
        """calculate the increase(s) in modularity if node is moved to other
        communities
        deltamod = inC - totc * ki / total_weight"""
        noded = part.node_degree(node)
        dnc = part.node_degree_by_community(node)
        totc = self._communities_nodes_alledgesw(part, node)
        total_weight = part.total_edge_weight
        # cast to arrays to improve calc
        dnc = np.array(dnc)
        totc = np.array(totc)
        return dnc - totc*noded / (total_weight*2)

    @staticmethod
    def _communities_without_node(part, node):
        """ returns a version of the partition with the node
        removed, may result in empty communities"""
        node_comm = part.get_node_community(node)
        newpart = copy.deepcopy(part.communities)
        newpart[node_comm].remove(node)
        return newpart

    def _communities_nodes_alledgesw(self, part, removed_node):
        """ returns the sum of all weighted edges to nodes in each
        community, once the removed_node is removed
        this refers to totc in Blondel paper"""
        comm_wo_node = self._communities_without_node(part, removed_node)
        weights = [0] * len(comm_wo_node)
        ## make a list of all nodes degree weights
        all_degree_weights = part.graph.degree(weight='weight').values()
        all_degree_weights = np.array(all_degree_weights)
        for val, nodeset in enumerate(comm_wo_node):
            node_index = np.array(list(nodeset)) #index of nodes in community
            #sum the weighted degree of nodes in community
            if len(node_index)<1:
                continue
            weights[val] = np.sum(all_degree_weights[node_index])
        return weights

    @staticmethod
    def _move_node(part, node, new_comm):
        """generate a new partition with node put into new community
        designated by index (new_comm) into existing part.communities"""
        ## copy
        new_community = [x.copy() for x in part.communities]
        ## update
        curr_node_comm = part.get_node_community(node)
        ## remove
        new_community[curr_node_comm].remove(node)
        new_community[new_comm].add(node)
        # Remove any empty sets from ne
        new_community = [x for x in new_community if len(x) > 0]
        return WeightedPartition(part.graph, new_community)

    def _partitions_from_dendogram(self, dendo):
        """ returns community partitions based on results in dendogram
        """
        all_partitions = []
        init_part = dendo[0].communities
        all_partitions.append(init_part)
        for partition in dendo[1:]:
            init_part = self._combine(init_part, partition.communities)
            all_partitions.append(init_part)
        return all_partitions

    @staticmethod
    def _combine(prev, next):
        """combines nodes in sets (prev) based on mapping defined by
        (next) (which now treats a previous communitity as a node)
        but maintains specification of all original nodes

        Parameters
        ----------
        prev : list of sets
            communities partition
        next : list of sets
            next level communities partition

        Examples
        --------
        >>> prev = [set([0,1,2]), set([3,4]), set([5,6])]
        >>> next = [set([0,1]), set([2])]
        >>> result = _combine(prev, next)
        [set([0, 1, 2, 3, 4]), set([5,6])]
        """
        expected_len = np.max([x for sublist in next for x in sublist])
        if not len(prev) == expected_len + 1:
            raise ValueError('Number of nodes in next does not'\
                ' match number of communities in prev')
        ret = []
        for itemset in next:
            newset = set()
            for tmps in itemset:
                newset.update(prev[tmps])
            ret.append(newset)
        return ret


def meta_graph(partition):
    """creates a new graph object based on input graph and partition

    Takes WeightedPartition object with specified communities and
    creates a new graph object where
    1. communities are now the nodes in the new graph
    2. the new edges are created based on the node to node connections (weights)
        from communities in the original graph, and weighted accordingly,
        (this includes self-loops)

    Returns
    -------
    metagraph : networkX graph
    mapping : dict
        dict showing the mapping from newnode -> original community nodes
    """
    metagraph = nx.Graph()
    # new nodes are communities
    newnodes = [val for val,_ in enumerate(partition.communities)]
    mapping = dict((val,nodes) for val,nodes in enumerate(partition.communities))
    metagraph.add_nodes_from(newnodes, weight=0.0)

    for node1, node2, data in partition.graph.edges_iter(data=True):
        node1_community = partition.get_node_community(node1)
        node2_community = partition.get_node_community(node2)
        try:
            tmpw = metagraph[node1_community][node2_community]['weight']
        except KeyError:
            tmpw = 0
        metagraph.add_edge(
            node1_community,
            node2_community,
            weight = tmpw + data['weight'])

    return metagraph, mapping
