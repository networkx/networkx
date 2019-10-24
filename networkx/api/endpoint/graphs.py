from graphspace_python.api.config import GRAPHS_PATH
from graphspace_python.api.obj.api_response import APIResponse

class Graphs(object):
	"""Graphs endpoint class.

	Provides methods for graph related operations such as saving, fetching, updating and deleting graphs on GraphSpace.
	"""

	def __init__(self, client):
		self.client = client

	def post_graph(self, graph):
		"""Posts NetworkX graph to the requesting users account on GraphSpace.

		Args:
			graph (GSGraph or Graph): Object having graph details, such as name, graph_json, style_json, is_public, tags.

		Returns:
			Graph: Saved graph on GraphSpace.

		Raises:
			GraphSpaceError: If error response is received from the GraphSpace API.

		Example:
			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Creating a graph
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.set_name('My Sample Graph')
			>>> G.set_tags(['sample'])
			>>> G.add_node('a', popup='sample node popup text', label='A')
			>>> G.add_node('b', popup='sample node popup text', label='B')
			>>> G.add_edge('a', 'b', directed=True, popup='sample edge popup')
			>>> G.add_edge_style('a', 'b', directed=True, edge_style='dotted')
			>>> # Saving graph on GraphSpace
			>>> graphspace.post_graph(G)

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#creating-a-graph>`_ for more about posting graphs.
		"""
		data = graph.json()
		data.update({'owner_email': self.client.username})
		return APIResponse('graph',
			self.client._make_request("POST", GRAPHS_PATH, data=data)
		).graph

	def get_graph(self, graph_name=None, graph_id=None, owner_email=None):
		"""Get a graph with the given graph_name or graph_id.

		Args:
			graph_name (str, optional): Name of the graph to be fetched. Defaults to None.
			graph_id (int, optional): ID of the graph to be fetched. Defaults to None.
			owner_email (str, optional): Email of the owner of the graph. Defaults to None.

		Returns:
			Graph or None: Graph object, if graph with the given 'graph_name' or 'graph_id' exists; otherwise None.

		Raises:
			Exception: If both 'graph_name' and 'graph_id' are None.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Getting a graph by name:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Fetching a graph
			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> graph.get_name()
			u'My Sample Graph'

			Getting a graph by id:

			>>> graph = graphspace.get_graph(graph_id=65930)
			>>> graph.get_name()
			u'My Sample Graph'

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#fetching-a-graph-from-graphspace>`_ for more about fetching graphs.
		"""
		if graph_id is not None:
			graph_by_id_path = GRAPHS_PATH + str(graph_id)
			return APIResponse('graph',
				self.client._make_request("GET", graph_by_id_path)
			).graph

		if graph_name is not None:
			query = {
				'owner_email': self.client.username if owner_email is None else owner_email,
				'names[]': graph_name
			}
			if owner_email is not None and owner_email != self.client.username:
				query.update({'is_public': 1})
			response = self.client._make_request("GET", GRAPHS_PATH, url_params=query)
			if response.get('total', 0) > 0:
				graph = response.get('graphs')[0]
				graph_by_id_path = GRAPHS_PATH + str(graph.get('id'))
				return APIResponse('graph',
					self.client._make_request("GET", graph_by_id_path)
				).graph
			else:
				return None

		raise Exception('Both graph_id and graph_name can\'t be none!')

	def get_public_graphs(self, tags=None, limit=20, offset=0):
		"""Get public graphs.

		Args:
			tags (List[str], optional): Search for graphs with the given given list of tag names.
				In order to search for graphs with given tag as a substring, wrap the name of the tag with percentage symbol.
				For example, %xyz% will search for all graphs with 'xyz' in their tag names. Defaults to None.
			offset (int, optional): Offset the list of returned entities by this number. Defaults to 0.
			limit (int, optional): Number of entities to return. Defaults to 20.

		Returns:
		 	List[Graph]: List of public graphs.

		Raises:
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Getting public graphs:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Fetching public graphs
			>>> graphs = graphspace.get_public_graphs(limit=5)
			>>> graphs[0].get_name()
			u'Wnt-Pathway-Reconstruction'

			Getting public graphs by tags:

			>>> graphs = graphspace.get_public_graphs(tags=['Kegg-networks'], limit=5)
			>>> graphs[0].get_name()
			u'KEGG-Wnt-signaling-pathway-with-ranks'
		"""
		query = {
			'is_public': 1,
			'limit': limit,
			'offset': offset
		}

		if tags is not None:
			query.update({'tags[]': tags})

		return APIResponse('graph',
			self.client._make_request("GET", GRAPHS_PATH, url_params=query)
		).graphs

	def get_shared_graphs(self, tags=None, limit=20, offset=0):
		"""Get graphs shared with the groups where requesting user is a member.

		Args:
			tags (List[str], optional): Search for graphs with the given given list of tag names.
				In order to search for graphs with given tag as a substring, wrap the name of the tag with percentage symbol.
				For example, %xyz% will search for all graphs with 'xyz' in their tag names. Defaults to None.
			offset (int, optional): Offset the list of returned entities by this number. Defaults to 0.
			limit (int, optional): Number of entities to return. Defaults to 20.

		Returns:
		 	List[Graph]: List of shared graphs.

		Raises:
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Getting shared graphs:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Fetching shared graphs
			>>> graphs = graphspace.get_shared_graphs(limit=5)
			>>> graphs[0].get_name()
			u'KEGG-Wnt-signaling-pathway'

			Getting shared graphs by tags:

			>>> graphs = graphspace.get_shared_graphs(tags=['Kegg-networks'], limit=5)
			>>> graphs[0].get_name()
			u'KEGG-Wnt-signaling-pathway'
		"""
		query = {
			'member_email': self.client.username,
			'limit': limit,
			'offset': offset
		}

		if tags is not None:
			query.update({'tags[]': tags})

		return APIResponse('graph',
			self.client._make_request("GET", GRAPHS_PATH, url_params=query)
		).graphs

	def get_my_graphs(self, tags=None, limit=20, offset=0):
		"""Get graphs created by the requesting user.

		Args:
			tags (List[str], optional): Search for graphs with the given given list of tag names.
				In order to search for graphs with given tag as a substring, wrap the name of the tag with percentage symbol.
				For example, %xyz% will search for all graphs with 'xyz' in their tag names. Defaults to None.
			offset (int, optional): Offset the list of returned entities by this number. Defaults to 0.
			limit (int, optional): Number of entities to return. Defaults to 20.

		Returns:
		 	List[Graph]: List of graphs owned by the requesting user.

		Raises:
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Getting your graphs:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Fetching my graphs
			>>> graphs = graphspace.get_my_graphs(limit=5)
			>>> graphs[0].get_name()
			u'test'

			Getting your graphs by tags:

			>>> graphs = graphspace.get_my_graphs(tags=['Kegg-networks'], limit=5)
			>>> graphs[0].get_name()
			u'KEGG-Wnt-signaling-pathway'
		"""
		query = {
			'owner_email': self.client.username,
			'limit': limit,
			'offset': offset
		}

		if tags is not None:
			query.update({'tags[]': tags})

		return APIResponse('graph',
			self.client._make_request("GET", GRAPHS_PATH, url_params=query)
		).graphs

	def delete_graph(self, graph_name=None, graph_id=None, graph=None):
		"""Delete a graph from GraphSpace provided the graph_name, graph_id or the graph object itself.

		Args:
			graph_name (str, optional): Name of the graph to be deleted. Defaults to None.
			graph_id (int, optional): ID of the graph to be deleted. Defaults to None.
			graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.

		Returns:
		 	str: Success/Error Message from GraphSpace.

		Raises:
			Exception: If both 'graph_name' and 'graph_id' are None and graph object has no
				'name' or 'id' attribute; or if graph doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Deleting a graph by name:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Deleting a graph
			>>> graphspace.delete_graph(graph_name='My Sample Graph')
			u'Successfully deleted graph with id=65930'

			Deleting a graph by id:

			>>> graphspace.delete_graph(graph_id=65930)
			u'Successfully deleted graph with id=65930'

			Deleting a graph by passing graph object itself as param:

			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> graphspace.delete_graph(graph=graph)
			u'Successfully deleted graph with id=65930'

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#deleting-a-graph-on-graphspace>`_ for more about deleting graphs.
		"""
		if graph is not None:
			if hasattr(graph, 'id'):
				graph_id = graph.id
			elif hasattr(graph, 'name'):
				graph_name = graph.name

		if graph_id is not None:
			graph_by_id_path = GRAPHS_PATH + str(graph_id)
			response = self.client._make_request("DELETE", graph_by_id_path)
			return response['message']

		if graph_name is not None:
			graph = self.get_graph(graph_name=graph_name)
			if graph is None or graph.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_by_id_path = GRAPHS_PATH + str(graph.id)
				response = self.client._make_request("DELETE", graph_by_id_path)
				return response['message']

		raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute!')

	def update_graph(self, graph, graph_name=None, graph_id=None, owner_email=None):
		"""Update a graph on GraphSpace with the provided graph object. If graph_name or graph_id
		is also provided then the update will be performed for that graph having the given name or id.

		Args:
			graph (GSGraph or Graph): Object having graph details, such as name, graph_json, style_json, is_public, tags.
			graph_name (str, optional): Name of the graph to be updated. Defaults to None.
			graph_id (int, optional): ID of the graph to be updated. Defaults to None.
			owner_email (str, optional): Email of owner of the graph. Defaults to None.

		Returns:
		 	Graph: Updated graph on GraphSpace.

		Raises:
			Exception: If both 'graph_name' and 'graph_id' are None and graph object has no
				'name' or 'id' attribute; or if graph doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Updating a graph by creating a new graph and replacing the existing graph:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Creating the new graph
			>>> G = GSGraph()
			>>> G.add_node('a', popup='sample node popup text', label='A updated')
			>>> G.add_node('b', popup='sample node popup text', label='B updated')
			>>> G.add_edge('a', 'b', directed=True, popup='sample edge popup')
			>>> G.add_edge_style('a', 'b', directed=True, edge_style='dotted')
			>>> G.set_name('My Sample Graph')
			>>> G.set_is_public(1)
			>>> # Updating to replace the existing graph
			>>> graphspace.update_graph(G)

			Another way of updating a graph by fetching and editing the existing graph:

			>>> # Fetching the graph
			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> # Modifying the fetched graph
			>>> graph.add_node('z', popup='sample node popup text', label='Z')
			>>> graph.add_node_style('z', shape='ellipse', color='green', width=90, height=90)
			>>> graph.add_edge('a', 'z', directed=True, popup='sample edge popup')
			>>> graph.set_is_public(1)
			>>> # Updating graph
			>>> graphspace.update_graph(graph)

			If you also provide 'graph_name' or 'graph_id' as param then the update will
			be performed for that graph having the given name or id:

			>>> graphspace.update_graph(G, graph_id=65930)

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#updating-a-graph-on-graphspace>`_ for more about updating graphs.
		"""
		if graph_id is not None or hasattr(graph, 'id'):
			graph_id = graph_id if graph_id is not None else graph.id
			graph_by_id_path = GRAPHS_PATH + str(graph_id)
			return APIResponse('graph',
				self.client._make_request("PUT", graph_by_id_path, data=graph.json())
			).graph

		if graph_name is not None or hasattr(graph, 'name'):
			graph_name = graph_name if graph_name is not None else graph.name
			graph1 = self.get_graph(graph_name=graph_name, owner_email=owner_email)
			if graph1 is None or graph1.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_by_id_path = GRAPHS_PATH + str(graph1.id)
				return APIResponse('graph',
					self.client._make_request("PUT", graph_by_id_path, data=graph.json())
				).graph

		raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute!')

	def publish_graph(self, graph_name=None, graph_id=None, graph=None):
		"""Makes a graph publicly viewable.

		Args:
			graph_name (str, optional): Name of the graph. Defaults to None.
			graph_id (int, optional): ID of the graph. Defaults to None.
			graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.

		Returns:
		 	Graph: Updated graph on GraphSpace.

		Raises:
			Exception: If both 'graph_name' and 'graph_id' are None and graph object has no
				'name' or 'id' attribute; or if graph doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Make graph public by name:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Publishing the graph
			>>> graph = graphspace.publish_graph(graph_name='My Sample Graph')
			>>> graph.get_is_public()
			1

			Make graph public by id:

			>>> graph = graphspace.publish_graph(graph_id=65930)
			>>> graph.get_is_public()
			1

			Make graph public by passing graph object itself as param:

			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> graphspace.publish_graph(graph=graph)

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#making-a-graph-public-on-graphspace>`_ for more about making a graph public.
		"""
		if graph is not None:
			if hasattr(graph, 'id'):
				graph_id = graph.id
			elif hasattr(graph, 'name'):
				graph_name = graph.name

		if graph_id is not None:
			graph_by_id_path = GRAPHS_PATH + str(graph_id)
			return APIResponse('graph',
				self.client._make_request("PUT", graph_by_id_path, data={'is_public': 1})
			).graph

		if graph_name is not None:
			graph = self.get_graph(graph_name=graph_name)
			if graph is None or graph.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_by_id_path = GRAPHS_PATH + str(graph.id)
				return APIResponse('graph',
					self.client._make_request("PUT", graph_by_id_path, data={'is_public': 1})
				).graph

		raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute!')

	def unpublish_graph(self, graph_name=None, graph_id=None, graph=None):
		"""Makes a graph privately viewable.

		Args:
			graph_name (str, optional): Name of the graph. Defaults to None.
			graph_id (int, optional): ID of the graph. Defaults to None.
			graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.

		Returns:
		 	Graph: Updated graph on GraphSpace.

		Raises:
			Exception: If both 'graph_name' and 'graph_id' are None and graph object has no
				'name' or 'id' attribute; or if graph doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Make graph private by name:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Unpublishing the graph
			>>> graph = graphspace.unpublish_graph(graph_name='My Sample Graph')
			>>> graph.get_is_public()
			0

			Make graph private by id:

			>>> graph = graphspace.unpublish_graph(graph_id=65930)
			>>> graph.get_is_public()
			0

			Make graph private by passing graph object itself as param:

			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> graphspace.unpublish_graph(graph=graph)

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#making-a-graph-private-on-graphspace>`_ for more about making a graph private.
		"""
		if graph is not None:
			if hasattr(graph, 'id'):
				graph_id = graph.id
			elif hasattr(graph, 'name'):
				graph_name = graph.name

		if graph_id is not None:
			graph_by_id_path = GRAPHS_PATH + str(graph_id)
			return APIResponse('graph',
				self.client._make_request("PUT", graph_by_id_path, data={'is_public': 0})
			).graph

		if graph_name is not None:
			graph = self.get_graph(graph_name=graph_name)
			if graph is None or graph.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_by_id_path = GRAPHS_PATH + str(graph.id)
				return APIResponse('graph',
					self.client._make_request("PUT", graph_by_id_path, data={'is_public': 0})
				).graph

		raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute!')

	def set_default_graph_layout(self, graph_name=None, graph_id=None, graph=None, layout_name=None, layout_id=None, layout=None):
		"""Set a default layout (provided the layout_name, layout_id or layout object) for a graph
		with given graph_name, graph_id or graph object itself.

		Args:
			graph_name (str, optional): Name of the graph. Defaults to None.
			graph_id (int, optional): ID of the graph. Defaults to None.
			graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.
			layout_name (str, optional): Name of the layout. Defaults to None.
			layout_id (int, optional): ID of the layout. Defaults to None.
			layout (GSLayout or Layout): Object having layout details, such as name, is_shared, style_json, positions_json.

		Returns:
		 	Graph: Updated graph on GraphSpace.

		Raises:
			Exception: If both 'layout_name' and 'layout_id' are None and layout object has no
				'name' or 'id' attribute; or if both 'graph_name' and 'graph_id' are None and neither graph object has
				'name' or 'id' attribute nor layout object has 'graph_id' attribute; or if graph or layout doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Setting a default layout when graph name is known:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Setting default layout for the graph
			>>> graph = graphspace.set_default_graph_layout(graph_name='My Sample Graph', layout_id=1087)
			>>> graph.default_layout_id
			1087

			Setting a default layout when graph id is known:

			>>> graph = graphspace.set_default_graph_layout(graph_id=65930, layout_id=1087)
			>>> graph.default_layout_id
			1087

			Setting a default layout when graph object is passed as param:

			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> graph = graphspace.set_default_graph_layout(graph=graph, layout_id=1087)
			>>> graph.default_layout_id
			1087

			Setting a default layout by passing layout name:

			>>> graph = graphspace.set_default_graph_layout(graph_id=65930, layout_name='My Sample Layout')
			>>> graph.default_layout_id
			1087

			Setting a default layout by only passing layout object as param:

			>>> layout = graphspace.get_graph_layout(graph_id=65930, layout_name='My Sample Layout')
			>>> graph = graphspace.set_default_graph_layout(layout=layout)
			>>> graph.default_layout_id
			1087

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#setting-a-default-layout-for-a-graph>`_ for more about setting default graph layout.
		"""
		if graph is not None:
			if hasattr(graph, 'id'):
				graph_id = graph.id
			elif hasattr(graph, 'name'):
				graph_name = graph.name

		if hasattr(layout, 'graph_id'):
			graph_id = layout.graph_id

		if graph_id is None and graph_name is None:
			raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute and layout object has no \'graph_id\' attribute!')

		if layout is not None:
			if hasattr(layout, 'id'):
				layout_id = layout.id
			elif hasattr(layout, 'name'):
				layout_name = layout.name

		if layout_id is None and layout_name is None:
			raise Exception('Both layout_id and layout_name can\'t be none when layout object has no \'name\' or \'id\' attribute!')

		if layout_id is None:
			layout = self.client.get_graph_layout(layout_name=layout_name, graph_id=graph_id)
			if layout is None or layout.id is None:
				raise Exception('Layout with name `%s` of graph with graph_id=%s doesnt exist for user `%s`!' % (layout_name, graph_id, self.client.username))
			else:
				layout_id = layout.id

		if graph_id is not None:
			graph_by_id_path = GRAPHS_PATH + str(graph_id)
			return APIResponse('graph',
				self.client._make_request("PUT", graph_by_id_path, data={'default_layout_id': layout_id})
			).graph

		if graph_name is not None:
			graph = self.get_graph(graph_name=graph_name)
			if graph is None or graph.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_by_id_path = GRAPHS_PATH + str(graph.id)
				return APIResponse('graph',
					self.client._make_request("PUT", graph_by_id_path, data={'default_layout_id': layout_id})
				).graph

	def unset_default_graph_layout(self, graph_name=None, graph_id=None, graph=None):
		"""Unsets the current default layout of a graph provided the graph_name, graph_id or graph object itself.

		Args:
			graph_name (str, optional): Name of the graph. Defaults to None.
			graph_id (int, optional): ID of the graph. Defaults to None.
			graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.

		Returns:
		 	Graph: Updated graph on GraphSpace.

		Raises:
			Exception: If both 'graph_name' and 'graph_id' are None and graph object has no
				'name' or 'id' attribute; or if graph doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Unset default graph layout by graph name:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Unset the default graph layout
			>>> graph = graphspace.unset_default_graph_layout(graph_name='My Sample Graph')
			>>> assert graph.default_layout_id is None

			Unset default graph layout by graph id:

			>>> graph = graphspace.unset_default_graph_layout(graph_id=65930)

			Unset default graph layout by graph object:

			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> graph = graphspace.unset_default_graph_layout(graph=graph)

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#unset-default-layout-for-a-graph>`_ for more about unsetting a default graph layout.
		"""
		if graph is not None:
			if hasattr(graph, 'id'):
				graph_id = graph.id
			elif hasattr(graph, 'name'):
				graph_name = graph.name

		if graph_id is not None:
			graph_by_id_path = GRAPHS_PATH + str(graph_id)
			return APIResponse('graph',
				self.client._make_request("PUT", graph_by_id_path, data={'default_layout_id': 0})
			).graph

		if graph_name is not None:
			graph = self.get_graph(graph_name=graph_name)
			if graph is None or graph.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_by_id_path = GRAPHS_PATH + str(graph.id)
				return APIResponse('graph',
					self.client._make_request("PUT", graph_by_id_path, data={'default_layout_id': 0})
				).graph

		raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute!')
