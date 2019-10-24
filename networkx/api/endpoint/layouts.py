from graphspace_python.api.config import LAYOUTS_PATH
from graphspace_python.api.obj.api_response import APIResponse

class Layouts(object):
	"""Layouts endpoint class.

	Provides methods for layout related operations such as saving, fetching, updating and deleting layouts on GraphSpace.
	"""

	def __init__(self, client):
		self.client = client

	def post_graph_layout(self, layout, graph_name=None, graph_id=None, graph=None):
		"""Create a layout for a graph provided the graph_name, graph_id or the graph object itself.

		Args:
			layout (GSLayout or Layout): Object having layout details, such as name, is_shared, style_json, positions_json.
			graph_name (str, optional): Name of the graph. Defaults to None.
			graph_id (int, optional): ID of the graph. Defaults to None.
			graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.

		Returns:
		 	Layout: Saved layout on GraphSpace.

		Raises:
			Exception: If both 'graph_name' and 'graph_id' are None and graph object has no
				'name' or 'id' attribute; or if graph doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Saving a layout when graph id is known:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Creating a layout
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.set_node_position('a', y=38.5, x=67.3)
			>>> L.add_node_style('a', shape='ellipse', color='green', width=60, height=60)
			>>> L.set_name('My Sample Layout')
			>>> L.set_is_shared(1)
			>>> # Saving layout on GraphSpace
			>>> graphspace.post_graph_layout(L, graph_id=65390)

			Saving a layout when graph name is known:

			>>> graphspace.post_graph_layout(L, graph_name='My Sample Graph')

			Saving a layout by passing graph object itself as param:

			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> graphspace.post_graph_layout(L, graph=graph)

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#creating-a-layout>`_ for more about posting layouts.
		"""
		if graph is not None:
			if hasattr(graph, 'id'):
				graph_id = graph.id
			elif hasattr(graph, 'name'):
				graph_name = graph.name

		if graph_id is None and graph_name is None:
			raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute!')

		if graph_id is None:
			graph = self.client.get_graph(graph_name=graph_name)
			if graph is None or graph.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_id = graph.id

		data = layout.json()
		data.update({'graph_id': graph_id, 'owner_email': self.client.username})
		layouts_path = LAYOUTS_PATH.format(graph_id)
		return APIResponse('layout',
			self.client._make_request("POST", layouts_path, data=data)
		).layout

	def update_graph_layout(self, layout, layout_name=None, layout_id=None, graph_name=None, graph_id=None, graph=None, owner_email=None):
		"""Update a layout with given layout_id or layout_name for a graph with the given
		graph_name, graph_id or the graph object itself.

		Args:
			layout (GSLayout or Layout): Object having layout details, such as name, is_shared, style_json, positions_json.
			layout_name (str, optional): Name of the layout to be updated. Defaults to None.
			layout_id (int, optional): ID of the layout to be updated. Defaults to None.
			graph_name (str, optional): Name of the graph. Defaults to None.
			graph_id (int, optional): ID of the graph. Defaults to None.
			graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.
			owner_email (str, optional): Email of owner of layout. Defaults to None.

		Returns:
		 	Layout: Updated layout on GraphSpace.

		Raises:
			Exception: If both 'layout_name' and 'layout_id' are None and layout object has no
				'name' or 'id' attribute; or if both 'graph_name' and 'graph_id' are None and neither graph object has
				'name' or 'id' attribute nor layout object has 'graph_id' attribute; or if graph or layout doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Updating a layout by creating a new layout and replacing the existing layout:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Creating the new layout
			>>> L = GSLayout()
			>>> L.set_node_position('a', y=102, x=238.1)
			>>> L.add_node_style('a', shape='octagon', color='green', width=60, height=60)
			>>> L.set_name('My Sample Layout')
			>>> L.set_is_shared(1)
			>>> # Updating to replace the existing layout
			>>> graphspace.update_graph_layout(L, graph_id=65390)

			Another way of updating a layout by fetching and editing the existing layout:

			>>> # Fetching the layout
			>>> layout = graphspace.get_graph_layout(name='My Sample Layout')
			>>> # Modifying the fetched layout
			>>> layout.set_node_position('a', y=30, x=211)
			>>> layout.add_node_style('a', shape='roundrectangle', color='green', width=45, height=45)
			>>> layout.set_is_shared(0)
			>>> # Updating layout
			>>> graphspace.update_graph_layout(layout)

			If you also provide 'layout_name' or 'layout_id' as param then the update will
			be performed for that layout having the given name or id:

			>>> graphspace.update_graph_layout(L, layout_id=1087, graph_id=65390)

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#updating-a-layout-on-graphspace>`_ for more about updating layouts.
		"""
		if hasattr(layout, 'graph_id'):
			graph_id = layout.graph_id

		if graph is not None:
			if hasattr(graph, 'id'):
				graph_id = graph.id
			elif hasattr(graph, 'name'):
				graph_name = graph.name

		if graph_id is None and graph_name is None:
			raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute and layout object has no \'graph_id\' attribute!')

		if graph_id is None:
			graph = self.client.get_graph(graph_name=graph_name)
			if graph is None or graph.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_id = graph.id

		if layout_id is not None or hasattr(layout, 'id'):
			layout_id = layout_id if layout_id is not None else layout.id
			layout_by_id_path = LAYOUTS_PATH.format(graph_id) + str(layout_id)
			return APIResponse('layout',
				self.client._make_request("PUT", layout_by_id_path, data=layout.json())
			).layout

		if layout_name is not None or hasattr(layout, 'name'):
			layout_name = layout_name if layout_name is not None else layout.name
			layout1 = self.get_graph_layout(graph_id=graph_id, layout_name=layout_name, owner_email=owner_email)
			if layout1 is None or layout1.id is None:
				raise Exception('Layout with name `%s` of graph with graph_id=%s doesnt exist for user `%s`!' % (layout_name, graph_id, self.client.username))
			else:
				layout_by_id_path = LAYOUTS_PATH.format(graph_id) + str(layout1.id)
				return APIResponse('layout',
					self.client._make_request("PUT", layout_by_id_path, data=layout.json())
				).layout

		raise Exception('Both layout_id and layout_name can\'t be none when layout object has no \'name\' or \'id\' attribute!')

	def delete_graph_layout(self, layout_name=None, layout_id=None, layout=None, graph_name=None, graph_id=None, graph=None):
		"""Delete a layout with given layout_name, layout_id or layout object itself from the
		graph with the given graph_name, graph_id or the graph object.

		Args:
			layout_name (str, optional): Name of the layout to be deleted. Defaults to None.
			layout_id (int, optional): ID of the layout to be deleted. Defaults to None.
			layout (GSLayout or Layout): Object having layout details, such as name, is_shared, style_json, positions_json.
			graph_name (str, optional): Name of the graph. Defaults to None.
			graph_id (int, optional): ID of the graph. Defaults to None.
			graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.

		Returns:
		 	str: Success/Error Message from GraphSpace.

		Raises:
			Exception: If both 'layout_name' and 'layout_id' are None and layout object has no
				'name' or 'id' attribute; or if both 'graph_name' and 'graph_id' are None and neither graph object has
				'name' or 'id' attribute nor layout object has 'graph_id' attribute; or if graph or layout doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Deleting a layout by layout name:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Deleting a layout
			>>> graphspace.delete_graph_layout(layout_name='My Sample Layout', graph_id=65390)
			u'Successfully deleted layout with id=1087'

			Deleting a layout by layout id:

			>>> graphspace.delete_graph_layout(layout_id=1087, graph_id=65930)
			u'Successfully deleted layout with id=1087'

			Deleting a layout by passing layout object as param:

			>>> layout = graphspace.get_graph_layout(layout_name='My Sample Layout', graph_id=65390)
			>>> graphspace.delete_graph_layout(layout=layout)
			u'Successfully deleted layout with id=1087'

			Deleting a layout by passing graph name instead of id:

			>>> graphspace.delete_graph_layout(layout_id=1087, graph_name='My Sample Graph')
			u'Successfully deleted layout with id=1087'

			Deleting a layout by passing graph object as param:

			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> graphspace.delete_graph_layout(layout_id=1087, graph=graph)
			u'Successfully deleted layout with id=1087'

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#deleting-a-layout-on-graphspace>`_ for more about deleting layouts.
		"""
		if hasattr(layout, 'graph_id'):
			graph_id = layout.graph_id

		if graph is not None:
			if hasattr(graph, 'id'):
				graph_id = graph.id
			elif hasattr(graph, 'name'):
				graph_name = graph.name

		if graph_id is None and graph_name is None:
			raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute and layout object has no \'graph_id\' attribute!')

		if graph_id is None:
			graph = self.client.get_graph(graph_name=graph_name)
			if graph is None or graph.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_id = graph.id

		if layout is not None:
			if hasattr(layout, 'id'):
				layout_id = layout.id
			elif hasattr(layout, 'name'):
				layout_name = layout.name

		if layout_id is not None:
			layout_by_id_path = LAYOUTS_PATH.format(graph_id) + str(layout_id)
			response = self.client._make_request("DELETE", layout_by_id_path)
			return response['message']

		if layout_name is not None:
			layout = self.get_graph_layout(graph_id=graph_id, layout_name=layout_name)
			if layout is None or layout.id is None:
				raise Exception('Layout with name `%s` of graph with graph_id=%s doesnt exist for user `%s`!' % (layout_name, graph_id, self.client.username))
			else:
				layout_by_id_path = LAYOUTS_PATH.format(graph_id) + str(layout.id)
				response = self.client._make_request("DELETE", layout_by_id_path)
				return response['message']

		raise Exception('Both layout_id and layout_name can\'t be none when layout object has no \'name\' or \'id\' attribute!')

	def get_graph_layout(self, layout_name=None, layout_id=None, graph_name=None, graph_id=None, graph=None, owner_email=None):
		"""Get a layout with given layout_id or layout_name for the graph with given graph_id,
		graph_name or graph object.

		Args:
			layout_name (str, optional): Name of the layout to be fetched. Defaults to None.
			layout_id (int, optional): ID of the layout to be fetched. Defaults to None.
			graph_name (str, optional): Name of the graph. Defaults to None.
			graph_id (int, optional): ID of the graph. Defaults to None.
			graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.
			owner_email (str, optional): Email of owner of layout. Defaults to None.

		Returns:
		 	Layout or None: Layout object, if layout with the given 'layout_name' or 'layout_id' exists; otherwise None.

		Raises:
			Exception: If both 'layout_name' and 'layout_id' are None; or if both 'graph_name'
				and 'graph_id' are None and graph object has no 'name' or 'id' attribute; or if
				graph doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Getting a layout by name:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Fetching a layout
			>>> layout = graphspace.get_graph_layout(layout_name='My Sample Layout', graph_id=65390)
			>>> layout.get_name()
			u'My Sample Layout'

			Getting a layout by id:

			>>> layout = graphspace.get_graph_layout(layout_id=1087, graph_id=65390)
			>>> layout.get_name()
			u'My Sample Layout'

			Getting a layout by providing graph name:

			>>> layout = graphspace.get_graph_layout(layout_id=1087, graph_name='My Sample Graph')
			>>> layout.get_name()
			u'My Sample Layout'

			Getting a layout by providing graph object as param:

			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> layout = graphspace.get_graph_layout(layout_id=1087, graph=graph)
			>>> layout.get_name()
			u'My Sample Layout'

		Note:
			Refer to the `tutorial <../tutorial/tutorial.html#fetching-a-layout-from-graphspace>`_ for more about fetching layouts.
		"""
		if graph is not None:
			if hasattr(graph, 'id'):
				graph_id = graph.id
			elif hasattr(graph, 'name'):
				graph_name = graph.name

		if graph_id is None and graph_name is None:
			raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute!')

		if graph_id is None:
			graph = self.client.get_graph(graph_name=graph_name)
			if graph is None or graph.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_id = graph.id

		if layout_id is not None:
			layout_by_id_path = LAYOUTS_PATH.format(graph_id) + str(layout_id)
			return APIResponse('layout',
				self.client._make_request("GET", layout_by_id_path)
			).layout

		if layout_name is not None:
			query = {
				'owner_email': self.client.username if owner_email is None else owner_email,
				'name': layout_name
			}
			if owner_email is not None and owner_email != self.client.username:
				query.update({'is_shared': 1})
			layouts_path = LAYOUTS_PATH.format(graph_id)
			response = self.client._make_request("GET", layouts_path, url_params=query)
			if response.get('total', 0) > 0:
				return APIResponse('layout',
					response.get('layouts')[0]
				).layout
			else:
				return None

		raise Exception('Both layout_id and layout_name can\'t be none!')

	def get_my_graph_layouts(self, graph_name=None, graph_id=None, graph=None, limit=20, offset=0):
		"""Get layouts created by the requesting user for the graph with given graph_name, graph_id or graph object.

		Args:
			graph_name (str, optional): Name of the graph. Defaults to None.
			graph_id (int, optional): ID of the graph. Defaults to None.
			graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.
			offset (int, optional): Offset the list of returned entities by this number. Defaults to 0.
			limit (int, optional): Number of entities to return. Defaults to 20.

		Returns:
		 	List[Layout]: List of layouts owned by the requesting user.

		Raises:
			Exception: If both 'graph_name' and 'graph_id' are None and graph object has no
				'name' or 'id' attribute; or if graph doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Getting your graph layouts by graph id:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Fetching my graph layouts
			>>> layouts = graphspace.get_my_graph_layouts(graph_id=65390, limit=5)
			>>> layouts[0].get_name()
			u'My Sample Layout'

			Getting your graph layouts by graph name:

			>>> layouts = graphspace.get_my_graph_layouts(graph_name='My Sample Graph', limit=5)

			Getting your graph layouts by graph object itself:

			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> layouts = graphspace.get_my_graph_layouts(graph=graph, limit=5)
		"""
		if graph is not None:
			if hasattr(graph, 'id'):
				graph_id = graph.id
			elif hasattr(graph, 'name'):
				graph_name = graph.name

		if graph_id is None and graph_name is None:
			raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute!')

		if graph_id is None:
			graph = self.client.get_graph(graph_name=graph_name)
			if graph is None or graph.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_id = graph.id

		query = {
			'limit': limit,
			'offset': offset,
			'owner_email': self.client.username
		}

		layouts_path = LAYOUTS_PATH.format(graph_id)
		return APIResponse('layout',
			self.client._make_request("GET", layouts_path, url_params=query)
		).layouts

	def get_shared_graph_layouts(self, graph_name=None, graph_id=None, graph=None, limit=20, offset=0):
		"""Get layouts shared with the requesting user for the graph with given graph_name, graph_id or graph object.

		Args:
			graph_name (str, optional): Name of the graph. Defaults to None.
			graph_id (int, optional): ID of the graph. Defaults to None.
			graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.
			offset (int, optional): Offset the list of returned entities by this number. Defaults to 0.
			limit (int, optional): Number of entities to return. Defaults to 20.

		Returns:
		 	List[Layout]: List of layouts shared with the requesting user.

		Raises:
			Exception: If both 'graph_name' and 'graph_id' are None and graph object has no
				'name' or 'id' attribute; or if graph doesnot exist.
			GraphSpaceError: If error response is received from the GraphSpace API.

		Examples:
			Getting shared graph layouts by graph id:

			>>> # Connecting to GraphSpace
			>>> from graphspace_python.api.client import GraphSpace
			>>> graphspace = GraphSpace('user1@example.com', 'user1')
			>>> # Fetching shared graph layouts
			>>> layouts = graphspace.get_shared_graph_layouts(graph_id=65390, limit=5)
			>>> layouts[0].get_name()
			u'My Sample Layout'

			Getting shared graph layouts by graph name:

			>>> layouts = graphspace.get_shared_graph_layouts(graph_name='My Sample Graph', limit=5)

			Getting shared graph layouts by graph object itself:

			>>> graph = graphspace.get_graph(graph_name='My Sample Graph')
			>>> layouts = graphspace.get_shared_graph_layouts(graph=graph, limit=5)
		"""
		if graph is not None:
			if hasattr(graph, 'id'):
				graph_id = graph.id
			elif hasattr(graph, 'name'):
				graph_name = graph.name

		if graph_id is None and graph_name is None:
			raise Exception('Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute!')

		if graph_id is None:
			graph = self.client.get_graph(graph_name=graph_name)
			if graph is None or graph.id is None:
				raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (graph_name, self.client.username))
			else:
				graph_id = graph.id

		query = {
			'limit': limit,
			'offset': offset,
			'is_shared': 1
		}

		layouts_path = LAYOUTS_PATH.format(graph_id)
		return APIResponse('layout',
			self.client._make_request("GET", layouts_path, url_params=query)
		).layouts
