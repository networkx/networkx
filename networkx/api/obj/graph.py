from graphspace_python.api.obj.response_object import ResponseObject
from graphspace_python.graphs.classes.gsgraph import GSGraph


class Graph(ResponseObject, GSGraph):
	"""Graph object class.

    Encapsulates details of a graph received in response.

    Attributes:
        id (int): Id of graph.
        name (str): Name of graph.
        owner_email (str): Email of owner of graph.
        is_public (int): Accessibility status of graph. Has value 0 if graph is private, 1 if graph is public.
        style_json (dict): Json representation for graph style.
        graph_json (dict): Json representation for graph structure.
        tags (List[str]): Tags of graph.
        data (dict): Metadata of graph.
        node (dict): Json representation for nodes of graph.
        edge (dict): Json representation for edges of graph.
        default_layout_id (int or None): Id of default layout of graph.
        created_at (str): Timestamp of graph creation.
        updated_at (str): Timestamp of graph updation.
        url (str): URL of graph on GraphSpace.
    """

	_fields = [
		'id',
		'name',
		'owner_email',
		'is_public',
		'created_at',
		'updated_at',
		'tags',
		'style_json',
		'graph_json',
		'default_layout_id'
	]

	def __init__(self, response):
		"""Construct a new 'Graph' object having the attributes specified in '_fields'.

        Sets the graph data and also creates the nodes and edges for the GSGraph class.

        Args:
            response (dict): Json representation of graph details.
        """
		GSGraph.__init__(self)
		ResponseObject.__init__(self, response)
		self.url = 'http://graphspace.org/graphs/' + str(self.id)
		if self.graph_json is not None:
			self.set_data(self.graph_json['data'])
			self._assign_nodes_and_edges()

	def _assign_nodes_and_edges(self):
		"""Adds the nodes and edges of the fetched graph to the GSGraph class' nodes and edges.

        This will ensure that the nodes and edges of the fetched graph are not lost when
        get_graph_json() is called.
        """
		nodes = self.graph_json['elements']['nodes']
		for node in nodes:
			self.add_node(node['data']['id'], node['data'])
			if 'position' in node:
				self.positions_json.update({node['data']['id']: node['position']})
		edges = self.graph_json['elements']['edges']
		for edge in edges:
			self.add_edge(edge['data']['source'], edge['data']['target'], edge['data'])
