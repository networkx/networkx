import datetime
import networkx as nx
import re
from six import string_types
from networkx.exception import NetworkXError


class GSGraph(nx.DiGraph):
	"""GSGraph class.

	A GSGraph stores the details of a graph that is understood by GraphSpace.

	It stores nodes and edges of a graph with some data attributes in an organised json structure.

	It also stores the style attributes of the respective nodes and edges in an organised json structure.

	It holds the information about the graph such as name, tags and viewability status.

	It provides methods to define, modify and delete the details of the graph.

	Attributes:
		name (str): Name of graph.
		is_public (int): Visibility status of graph. Has value 0 if graph is private, 1 if graph is public.
		style_json (dict): Json representation for graph style.
		graph_json (dict): Json representation for graph structure.
		tags (List[str]): Tags of graph.
		data (dict): Metadata of graph.
		node (dict): Json representation for nodes of graph.
		edge (dict): Json representation for edges of graph.
	"""

	ALLOWED_NODE_SHAPES = ['rectangle', 'roundrectangle', 'ellipse', 'triangle',
						   'pentagon', 'hexagon', 'heptagon', 'octagon', 'star',
						   'diamond', 'vee', 'rhomboid']

	ALLOWED_NODE_BORDER_STYLES = ['solid', 'dotted', 'dashed', 'double']

	ALLOWED_NODE_BACKGROUND_REPEAT = ['no-repeat', 'repeat-x', 'repeat-y', 'repeat']

	ALLOWED_NODE_TEXT_TRANSFORM = ['none', 'uppercase', 'lowercase']

	ALLOWED_NODE_TEXT_WRAP = ['none', 'wrap']

	ALLOWED_TEXT_BACKROUND_SHAPE = ['rectangle', 'roundrectangle']

	ALLOWED_TEXT_HALIGN = ['left', 'center', 'right']

	ALLOWED_TEXT_VALIGN = ['top', 'center', 'bottom']

	## See http://js.cytoscape.org/#style/labels
	ALLOWED_TEXT_WRAP = ['wrap', 'none']

	## See http://js.cytoscape.org/#style/edge-arrow
	ALLOWED_ARROW_SHAPES = ['tee', 'triangle', 'triangle-tee', 'triangle-backcurve',
							'square', 'circle', 'diamond', 'none']

	## See http://js.cytoscape.org/#style/edge-line
	ALLOWED_EDGE_STYLES = ['solid', 'dotted', 'dashed']

	ALLOWED_ARROW_FILL = ['filled', 'hollow']

	NODE_COLOR_ATTRIBUTES = ['background-color', 'border-color', 'color',
							 'text-outline-color', 'text-shadow-color',
							 'text-border-color']

	EDGE_COLOR_ATTRIBUTES = ['line-color', 'source-arrow-color',
							 'mid-source-arrow-color', 'target-arrow-color',
							 'mid-target-arrow-color']

	def __init__(self, *args, **kwargs):
		"""Construct a new 'GSGraph' object.

		Args:
			*args: Variable length argument list.
			**kwargs: Arbitrary keyword arguments.
		"""
		super(GSGraph, self).__init__(*args, **kwargs)
		self.set_name('Graph ' + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
		self.tags = []
		self.data = {}
		self.positions_json = {}
		self.graph_json = self.get_graph_json()
		self.style_json = {'style': []}
		self.is_public = 0

	def json(self):
		"""Get the json representation of graph details.

		Returns:
			dict: Json representation of graph details.

		Examples:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.json()
			{'is_public': 0, 'style_json': {'style': []}, 'tags': [], 'name':
			'Graph 12:10PM on July 20, 2017', 'graph_json': {'elements': {'nodes': [],
			'edges': []}, 'data': {'name': 'Graph 12:10PM on July 20, 2017', 'tags': []}}}
			>>> G.set_name('My sample graph')
			>>> G.add_node('a', popup='sample node popup text', label='A')
			>>> G.add_node_style('a', shape='ellipse', color='red', width=90, height=90)
			>>> G.json()
			{'is_public': 0, 'style_json': {'style': [{'style': {'border-color': '#000000',
			'border-width': 1, 'height': 90, 'width': 90, 'shape': 'ellipse', 'border-style':
			'solid', 'text-wrap': 'wrap', 'text-halign': 'center', 'text-valign': 'center',
			'background-color': 'red'}, 'selector': 'node[name="a"]'}]}, 'tags': [], 'name':
			'My sample graph', 'graph_json': {'elements': {'nodes': [{'data': {'id': 'a',
			'popup': 'sample node popup text', 'name': 'a', 'label': 'A'}}], 'edges': []},
			'data': {'name': 'My sample graph', 'tags': []}}}
		"""
		data = {
			'name': self.get_name(),
			'is_public': self.get_is_public(),
			'graph_json': self.get_graph_json(),
			'style_json': self.get_style_json(),
			'tags': self.get_tags()
		}
		return data

	def get_graph_json(self):
		"""Computes the json representation for the graph structure from the graph
		nodes and edges and returns it.

		Returns:
			dict: Json representation of graph structure.

		Examples:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.get_graph_json()
			{'elements': {'nodes': [], 'edges': []}, 'data': {'name':
			'Graph 12:10PM on July 20, 2017', 'tags': []}}
			>>> G.set_name('My sample graph')
			>>> G.add_node('a', popup='sample node popup text', label='A')
			>>> G.add_node('b', popup='sample node popup text', label='B')
			>>> G.add_edge('a', 'b', directed=True, popup='sample edge popup')
			>>> G.get_graph_json()
			{'elements': {'nodes': [{'data': {'id': 'a', 'popup': 'sample node popup text',
			'name': 'a', 'label': 'A'}}, {'data': {'id': 'b', 'popup': 'sample node popup text',
			'name': 'b', 'label': 'B'}}], 'edges': [{'data': {'source': 'a', 'popup':
			'sample edge popup', 'is_directed': True, 'target': 'b'}}]}, 'data': {'name':
			'My sample graph', 'tags': []}}
		"""
		self.graph_json = {
			'data': self.get_data(),
			'elements': {
				'nodes': [],
				'edges': [],
			}
		}

		for node in self.nodes(data=True):
			node_attr = {'data': node[1]}
			if node[0] in self.positions_json:
				node_attr.update({'position': self.positions_json[node[0]]})
			node_attr['data'].update({'id': node[1].get('id', node[0])})
			node_attr['data'].update({'name': node[1].get('name', node[0])})
			self.graph_json['elements']['nodes'].append(node_attr)

		for edge in self.edges(data=True):
			edge_attr = {'data': edge[2]}
			edge_attr['data'].update({'source': edge[2].get('source', edge[0])})
			edge_attr['data'].update({'target': edge[2].get('target', edge[1])})
			edge_attr['data'].update({'is_directed': edge[2].get('is_directed', False)})
			self.graph_json['elements']['edges'].append(edge_attr)

		return self.graph_json

	def get_data(self):
		"""Computes the metadata of the graph and returns it.

		Returns:
			dict: Metadata of the graph.

		Examples:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.get_data()
			{'name': 'Graph 12:10PM on July 20, 2017', 'tags': []}
			>>> G.set_name('My sample graph')
			>>> G.set_tags(['sample','tutorial'])
			>>> G.get_data()
			{'name': 'My sample graph', 'tags': ['sample', 'tutorial']}
		"""
		data = {
			'name': self.name,
			'tags': self.tags
		}
		self.data.update(data)
		return self.data

	def get_style_json(self):
		"""Get the json representation for the graph style.

		Returns:
			dict: Json representation of graph style.

		Examples:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.get_style_json()
			{'style': []}
			>>> G.add_node_style('a', shape='ellipse', color='red', width=90, height=90)
			>>> G.get_style_json()
			{'style': [{'style': {'border-color': '#000000', 'border-width': 1, 'height': 90,
			'width': 90, 'shape': 'ellipse', 'border-style': 'solid', 'text-wrap': 'wrap',
			'text-halign': 'center', 'text-valign': 'center', 'background-color': 'red'},
			'selector': 'node[name="a"]'}]}
		"""
		return self.style_json

	def set_graph_json(self, graph_json):
		"""Set the json representation for the graph structure.

		Args:
			graph_json (dict): Json representation for the graph structure.

		Example:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> graph_json = {
			... 	'elements': {
			... 		'nodes': [
			... 			{
			... 				'data': {
			... 					'id': 'a',
			... 					'popup': 'sample node popup text',
			... 					'name': 'a',
			... 					'label': 'A'
			... 				}
			... 			}
			... 		],
			... 		'edges': []
			... 	},
			... 	'data': {
			... 		'name': 'My sample graph',
			... 		'tags': ['sample', 'tutorial']
			... 	}
			... }
			>>> G.set_graph_json(graph_json)
			>>> G.get_graph_json()
			{'elements': {'nodes': [{'data': {'id': 'a', 'popup': 'sample node popup text',
			'name': 'a', 'label': 'A'}}], 'edges': []}, 'data': {'name': 'My sample graph',
			'tags': ['sample', 'tutorial']}}
		"""
		self.graph_json = graph_json
		self.remove_nodes_from(self.nodes())
		if 'data' in graph_json:
			self.set_data(graph_json['data'])
		nodes = graph_json['elements']['nodes']
		for node in nodes:
			self.add_node(node['data']['id'], node['data'])
			if 'position' in node:
				self.positions_json.update({node['data']['id']: node['position']})
		edges = graph_json['elements']['edges']
		for edge in edges:
			self.add_edge(edge['data']['source'], edge['data']['target'], edge['data'])

	def set_style_json(self, style_json):
		"""Set the json representation for the graph style.

		Args:
			style_json (dict): Json representation for the graph style.

		Example:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> style_json = {
			... 	'style': [
			... 		{
			... 			'style': {
			... 				'border-color': '#000000',
			... 				'border-width': 1,
			... 				'height': 90,
			... 				'width': 90,
			... 				'shape': 'ellipse',
			... 				'border-style': 'solid',
			... 				'text-wrap': 'wrap',
			... 				'text-halign': 'center',
			... 				'text-valign': 'center',
			... 				'background-color': 'red'
			... 			},
			... 			'selector': 'node[name="a"]'
			... 		}
			... 	]
			... }
			>>> G.set_style_json(style_json)
			>>> G.get_style_json()
			{'style': [{'style': {'border-color': '#000000', 'border-width': 1, 'height': 90,
			'width': 90, 'shape': 'ellipse', 'border-style': 'solid', 'text-wrap': 'wrap',
			'text-halign': 'center', 'text-valign': 'center', 'background-color': 'red'},
			'selector': 'node[name="a"]'}]}
		"""
		GSGraph.validate_style_json(style_json)
		self.style_json = style_json

	def get_name(self):
		"""Get the name of graph.

		Returns:
			str: Name of graph.

		Examples:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.get_name()
			'Graph 01:22PM on July 20, 2017'
			>>> G.set_name('My sample graph')
			>>> G.get_name()
			'My sample graph'
		"""
		return self.name

	def set_name(self, name):
		"""Set the name of the graph.

		Args:
			name (str): Name of graph.

		Example:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.set_name('My sample graph')
			>>> G.get_name()
			'My sample graph'
		"""
		self.name = name

	def get_is_public(self):
		"""Get visibility status of the graph.

		Returns:
			int: Visibility status of graph. Either 0 or 1.

		Examples:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.get_is_public()
			0
			>>> G.set_is_public(1)
			>>> G.get_is_public()
			1
		"""
		return self.is_public

	def set_is_public(self, is_public=1):
		"""Set visibility status of the graph.

		Args:
			is_public (int, optional): Visibility status of graph. Defaults to 1.

		Raises:
			Exception: If 'is_public' is neither 0 nor 1.

		Examples:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.set_is_public() # By default takes param 'is_public' as 1.
			>>> G.get_is_public()
			1
			>>> G.set_is_public(0)
			>>> G.get_is_public()
			0
		"""
		if is_public not in [0, 1, True, False]:
			raise Exception("is_public should have value either 0 or 1 or should be boolean.")
		else:
			self.is_public = int(is_public)

	def set_data(self, data):
		"""Set the metadata of the graph.

		Args:
			data (dict): Key-value pairs describing the graph.

		Example:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.set_name('My sample graph')
			>>> G.set_tags(['sample'])
			>>> G.set_data({'description': 'A sample graph for demonstration purpose.'})
			>>> G.get_data()
			{'description': 'A sample graph for demonstration purpose.', 'name':
			'My sample graph', 'tags': ['sample']}
		"""
		self.data.update(data)
		if 'name' in data:
			self.set_name(self.data.get('name'))
		if 'tags' in data:
			self.set_tags(self.data.get('tags'))

	def get_tags(self):
		"""Get the tags for the graph.

		Returns:
			List[str]: List of tags of graph.

		Examples:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.get_tags()
			[]
			>>> G.set_tags(['sample', 'tutorial'])
			>>> G.get_tags()
			['sample', 'tutorial']
		"""
		return self.tags

	def set_tags(self, tags):
		"""Set the tags for the graph.

		Args:
			tags (List[str]): List of tags of graph.

		Example:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.set_tags(['sample', 'tutorial'])
			>>> G.get_tags()
			['sample', 'tutorial']
		"""
		self.tags = tags

	def add_edge(self, source, target, attr_dict=None, directed=False, popup=None, k=None, **attr):
		"""Add an edge to the graph.

		Args:
			source (str): Source node.
			target (str): Target node.
			attr_dict (dict, optional): Json representation of edge data. Defaults to None.
			directed (bool, optional): True if edge is directed, else False. Defaults to False.
			popup (str, optional): A string that will be displayed in a popup window when
				the user clicks the edge. This string can be HTML-formatted information,
				e.g., Gene Ontology annotations and database links for a protein; or types,
				mechanism, and database sources for an interaction.
			k (int, optional): An integer-valued attribute for the edge, which denotes a
				rank. Through this attribute, GraphSpace allows the user to filter nodes
				and edges in a network visualization.
			**attr: Arbitrary keyword arguments.

		Example:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.add_node('a', popup='sample node popup text', label='A')
			>>> G.add_node('b', popup='sample node popup text', label='B')
			>>> G.add_edge('a', 'b', directed=True, popup='sample edge popup')
			>>> G.edges(data=True)
			[('a', 'b', {'source': 'a', 'popup': 'sample edge popup',
			'is_directed': True, 'target': 'b'})]
		"""
		# set up attribute dict
		if attr_dict is None:
			attr_dict = attr
		else:
			try:
				attr_dict.update(attr)
			except AttributeError:
				raise NetworkXError("The attr_dict argument must be a dictionary.")

		if popup is not None:
			attr_dict.update({"popup": popup})
		if k is not None:
			attr_dict.update({"k": k})

		if attr_dict.get('is_directed', False) or directed:
			attr_dict.update({'is_directed': True})
		else:
			attr_dict.update({'is_directed': False})

		attr_dict.update({"source": source, "target": target})

		GSGraph.validate_edge_data_properties(data_properties=attr_dict, nodes_list=self.nodes())
		if float(nx.__version__) >= 2:
			super(GSGraph, self).add_edge(source, target, **attr_dict)
		else:
			super(GSGraph, self).add_edge(source, target, attr_dict)

	def add_node(self, node_name, attr_dict=None, parent=None, label=None, popup=None, k=None, **attr):
		"""Add a node to the graph.

		Args:
			node_name (str): Name of node.
			attr_dict (dict, optional): Json representation of node data. Defaults to None.
			parent (str, optional): Parent of the node, if any (for compound nodes). Defaults to None.
			label (str, optional): Label of node. Defaults to None.
			popup (str, optional): A string that will be displayed in a popup window when
				the user clicks the node. This string can be HTML-formatted information,
				e.g., Gene Ontology annotations and database links for a protein; or types,
				mechanism, and database sources for an interaction.
			k (int, optional): An integer-valued attribute for the node, which denotes a
				rank. Through this attribute, GraphSpace allows the user to filter nodes
				and edges in a network visualization.
			**attr: Arbitrary keyword arguments.

		Example:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.add_node('a', popup='sample node popup text', label='A')
			>>> G.add_node('b', popup='sample node popup text', label='B')
			>>> G.nodes(data=True)
			[('a', {'id': 'a', 'popup': 'sample node popup text', 'name': 'a',
			'label': 'A'}), ('b', {'id': 'b', 'popup': 'sample node popup text',
			'name': 'b', 'label': 'B'})]
		"""
		# set up attribute dict
		if attr_dict is None:
			attr_dict = attr
		else:
			try:
				attr_dict.update(attr)
			except AttributeError:
				raise NetworkXError("The attr_dict argument must be a dictionary.")

		if parent is not None:
			attr_dict.update({"parent": parent})
		if popup is not None:
			attr_dict.update({"popup": popup})
		if k is not None:
			attr_dict.update({"k": k})
		if label is not None:
			attr_dict.update({"label": label})

		attr_dict.update({"name": node_name, "id": node_name})

		GSGraph.validate_node_data_properties(data_properties=attr_dict, nodes_list=self.nodes())
		if float(nx.__version__) >= 2:
			super(GSGraph, self).add_node(node_name, **attr_dict)
		else:
			super(GSGraph, self).add_node(node_name, attr_dict)

	def add_node_style(self, node_name, attr_dict=None, content=None, shape='ellipse', color='#FFFFFF', height=None,
									   width=None, bubble=None, valign='center', halign='center', style="solid",
									   border_color='#000000', border_width=1):
		"""Add styling for a node belonging to the graph.

		Args:
			node_name (str): Name of node.
			attr_dict (dict, optional): Json representation of style of node. Defaults to None.
			shape (str, optional): Shape of node. Defaults to 'ellipse'. See :data:`ALLOWED_NODE_SHAPES` for more details.
			color (str, optional): Hexadecimal representation of the color (e.g., #FFFFFF) or color name. Defaults to white.
			height (int, optional): Height of the node's body, or None to determine height from the number of lines in the label. Defaults to None.
			width (int, optional): Width of the node's body, or None to determine width from length of label. Defaults to None.
			bubble (str, optional): Color of the text outline. Using this option gives a "bubble" effect; see the bubbleeffect() function. Defaults to None.
			valign (str, optional): Vertical alignment. Defaults to 'center'. See :data:`ALLOWED_TEXT_VALIGN` for more details.
			halign (str, optional): Horizontal alignment. Defaults to 'center'. See :data:`ALLOWED_TEXT_HALIGN` for more details.
			style (str, optional): Style of border. Defaults to 'solid'. If 'bubble' is specified, then style is overwritten. See :data:`ALLOWED_NODE_BORDER_STYLES` for more details.
			border_color (str, optional): Color of border. Defaults to '#000000'. If 'bubble' is specified, then style is overwritten.
			border_width (int, optional): Width of border. Defaults to 1. If 'bubble' is specified, then style is overwritten.

		Examples:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.add_node('a', popup='sample node popup text', label='A')
			>>> G.add_node_style('a', shape='ellipse', color='red', width=90, height=90)
			>>> G.add_node('b', popup='sample node popup text', label='B')
			>>> G.add_node_style('b', color='blue', width=90, height=90, border_color='#4f4f4f')
			>>> G.get_style_json()
			{'style': [{'style': {'border-color': '#000000', 'border-width': 1, 'height': 90,
			'width': 90, 'shape': 'ellipse', 'border-style': 'solid', 'text-wrap': 'wrap',
			'text-halign': 'center', 'text-valign': 'center', 'background-color': 'red'},
			'selector': 'node[name="a"]'}, {'style': {'border-color': '#4f4f4f', 'border-width': 1,
			'height': 90, 'width': 90, 'shape': 'ellipse', 'border-style': 'solid', 'text-wrap':
			'wrap', 'text-halign': 'center', 'text-valign': 'center', 'background-color': 'blue'},
			'selector': 'node[name="b"]'}]}
		"""
		attr_dict = attr_dict if attr_dict is not None else dict()

		selector = 'node[name="%s"]' % node_name

		style_properties = {}
		style_properties = GSGraph.set_node_shape_property(style_properties, shape)
		style_properties = GSGraph.set_node_color_property(style_properties, color)
		style_properties = GSGraph.set_node_label_property(style_properties, content)
		style_properties = GSGraph.set_node_width_property(style_properties, width)
		style_properties = GSGraph.set_node_height_property(style_properties, height)
		style_properties = GSGraph.set_node_vertical_alignment_property(style_properties, valign)
		style_properties = GSGraph.set_node_horizontal_alignment_property(style_properties, halign)
		style_properties = GSGraph.set_node_border_style_property(style_properties, style)
		style_properties = GSGraph.set_node_border_color_property(style_properties, border_color)
		style_properties = GSGraph.set_node_border_width_property(style_properties, border_width)

		# If bubble is specified, use the provided color,
		if bubble:
			style_properties = GSGraph.set_node_bubble_effect_property(style_properties, bubble, whitetext=False)

		style_properties.update(attr_dict)

		self.set_style_json({
			'style': self.get_style_json().get('style') + [{
				'selector': selector,
				'style': style_properties
			}]
		})

	def add_edge_style(self, source, target, attr_dict=None, directed=False, color='#000000', width=1.0, arrow_shape='triangle',
					   edge_style='solid', arrow_fill='filled'):
		"""Add styling for an edge whose source and target nodes are provided.

		Args:
			source (str): Unique ID of the source node.
			target (str): Unique ID of the target node.
			attr_dict (dict, optional): Json representation of style of edge. Defaults to None.
			color (str, optional): Hexadecimal representation of the color (e.g., #000000), or the color name. Defaults to black.
			directed (bool, optional): If True, draw the edge as directed. Defaults to False.
			width (float, optional): Width of the edge. Defaults to 1.0.
			arrow_shape (str, optional): Shape of arrow head. Defaults to 'triangle'. See :data:`ALLOWED_ARROW_SHAPES` for more details.
			edge_style (str, optional): Style of edge. Defaults to 'solid'. See :data:`ALLOWED_EDGE_STYLES` for more details.
			arrow_fill (str, optional): Fill of arrow. Defaults to 'filled'. See :data:`ALLOWED_ARROW_FILL` for more details.

		Examples:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.add_edge_style('a', 'b', directed=True, edge_style='dotted')
			>>> G.add_edge_style('b', 'c', arrow_shape='tee', arrow_fill='hollow')
			>>> G.get_style_json()
			{'style': [{'style': {'width': 1.0, 'line-color': '#000000', 'target-arrow-shape':
			'triangle', 'line-style': 'dotted', 'target-arrow-fill': 'filled', 'target-arrow-color':
			'#000000'}, 'selector': 'edge[source="a"][target="b"]'}, {'style': {'width': 1.0,
			'line-color': '#000000', 'target-arrow-shape': 'none', 'line-style': 'solid',
			'target-arrow-fill': 'hollow', 'target-arrow-color': '#000000'}, 'selector':
			'edge[source="b"][target="c"]'}]}
		"""
		style_properties = {}
		style_properties = GSGraph.set_edge_color_property(style_properties, color)
		style_properties = GSGraph.set_edge_width_property(style_properties, width)
		style_properties = GSGraph.set_edge_target_arrow_shape_property(style_properties, arrow_shape)
		style_properties = GSGraph.set_edge_directionality_property(style_properties, directed, arrow_shape)
		style_properties = GSGraph.set_edge_line_style_property(style_properties, edge_style)
		style_properties = GSGraph.set_edge_target_arrow_fill(style_properties, arrow_fill)

		attr_dict = attr_dict if attr_dict is not None else dict()

		selector = 'edge[source="%s"][target="%s"]' % (source, target)

		style_properties.update(attr_dict)

		self.set_style_json({
			'style': self.get_style_json().get('style') + [{
				'selector': selector,
				'style': style_properties
			}]
		})

	def add_style(self, selector, style_dict):
		"""Add styling for a given selector, for e.g., 'nodes', 'edges', etc.

		Args:
			selector (str): A selector functions similar to a CSS selector on DOM elements, but here it works on collections of graph elements.
			style_dict (dict): Key-value pair of style attributes and their values.

		Examples:
			>>> from graphspace_python.graphs.classes.gsgraph import GSGraph
			>>> G = GSGraph()
			>>> G.add_style('node', {'background-color': '#bbb', 'opacity': 0.8})
			>>> G.add_style('edge', {'line-color': 'green'})
			>>> G.get_style_json()
			{'style': [{'style': {'opacity': 0.8, 'background-color': '#bbb'}, 'selector':
			'node'}, {'style': {'line-color': 'green'}, 'selector': 'edge'}]}
		"""
		self.set_style_json({
			'style': self.get_style_json().get('style') + [{
				'selector': selector,
				'style': style_dict
			}]
		})

	def get_node_position(self, node_name):
		"""Get the x,y position of a node.

		Args:
			node_name (str): Name of the node.

		Returns:
		 	dict or None: Dict of x,y co-ordinates of the node, if node position is defined; otherwise None.

		"""
		return self.positions_json.get(node_name, None)

	def set_node_position(self, node_name, y, x):
		"""Set the x,y position of a node.

		Args:
			node_name (str): Name of the node.
			y (float): y co-ordinate of node.
			x (float): x co-ordinate of node.
		"""
		self.positions_json.update({
			node_name: {
				'y': y,
				'x': x
			}
		})

	def remove_node_position(self, node_name):
		"""Remove the x,y position of a node.

		Args:
			node_name (str): Name of the node.

		Raises:
			Exception: If node positions are undefined.
		"""
		if node_name not in self.positions_json.keys():
			raise Exception("Positions of node '%s' is undefined." % (node_name))
		else:
			del self.positions_json[node_name]

	####################################################################
	### NODE PROPERTY FUNCTIONS #################################################


	@staticmethod
	def set_node_label_property(node_properties, label):
		"""Set 'label' to 'node_properties' dict and return the 'node_properties' dict.
		The label is stored under 'content' in the node information. Also set wrap = 'wrap' so newlines are interpreted.

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			label (str): Text to display on node. Newline sequence will be interpreted as a line break.

		Returns:
			dict: Dictionary of node attributes.
		"""
		if label is not None:
			node_properties.update({'content': label})
		node_properties = GSGraph.set_node_wrap_property(node_properties, 'wrap')

		return node_properties

	@staticmethod
	def set_node_wrap_property(node_properties, wrap):
		"""Adding node wrap allows the newline sequence to be interpreted as a line break for the node.

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			wrap (str): String denoting the type of wrap: one of "wrap" or "none".

		Returns:
			dict: Dictionary of node attributes.

		Raises:
			Exception: If the wrap parameter is not one of the allowed wrap styles. See ALLOWED_NODE_TEXT_WRAP for more details.
		"""
		if wrap not in GSGraph.ALLOWED_NODE_TEXT_WRAP:
			raise Exception('"%s" is not an allowed text wrap style.' % (wrap))
		node_properties.update({'text-wrap': wrap})
		return node_properties

	@staticmethod
	def set_node_shape_property(node_properties, shape):
		"""Add a shape property "shape" to the node_properties.

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			shape (str): Shape of node.

		Returns:
			dict: Dictionary of node attributes.

		Raises:
			Exception: If the shape is not one of the allowed node shapes. See ALLOWED_NODE_SHAPES global variable.
		"""
		if shape not in GSGraph.ALLOWED_NODE_SHAPES:
			raise Exception('"%s" is not an allowed shape.' % (shape))
		node_properties.update({'shape': shape})
		return node_properties

	@staticmethod
	def set_node_color_property(node_properties, color):
		"""Add a background color to the node_properties.
		Color can be a name (e.g., 'black') or an HTML string (e.g., #00000).

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			color (str): Hexadecimal representation of the color (e.g., #FFFFFF) or color name.

		Returns:
			dict: Dictionary of node attributes.

		Raises:
			Exception: If the color is improperly formatted.
		"""
		error = GSGraph.check_color_hex(color)
		if error is not None:
			raise Exception(error)
		node_properties.update({'background-color': color})
		return node_properties

	@staticmethod
	def set_node_height_property(node_properties, height):
		"""Add a node height property to the node_properties.
		If the height is 'None', then the height of the node is determined by the number of newlines in the label that will be displayed.

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			height (int or None): Height of the node's body, or None to determine height from the number of lines in the label.

		Returns:
			dict: Dictionary of node attributes.
		"""
		if height == None:
			height = 'label'

		node_properties.update({'height': height})
		return node_properties

	@staticmethod
	def set_node_width_property(node_properties, width):
		"""Add a node width property to the node_properties.
		If the width is 'None', then the width of the node is determined by the length of the label.

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			width (int or None): Width of the node's body, or None to determine width from length of label.

		Returns:
			dict: Dictionary of node attributes.
		"""
		if width == None:
			## take the longest width of the label after interpreting newlines.
			width = 'label'
		node_properties.update({'width': width})
		return node_properties

	@staticmethod
	def set_node_bubble_effect_property(node_properties, color, whitetext=False):
		"""Add a "bubble effect" to the node by making the border color the same as the text outline color.

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			color (str): Hexadecimal representation of the text outline color (e.g., #FFFFFF) or a color name.
			whitetext (bool, optional): If True, text is colored white instead of black. Defaults to False.

		Returns:
			dict: Dictionary of node attributes.
		"""
		node_properties.update({'text-outline-color': color})
		node_properties = GSGraph.set_node_border_color_property(node_properties, color)
		# also make outline thicker and text larger
		node_properties.update({'text-outline-width': 4})
		if whitetext:
			node_properties.update({'color': 'white'})
		return node_properties

	@staticmethod
	def set_node_border_width_property(node_properties, border_width):
		"""Set the border width in node_properties.

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			border_width (int): Width of border.

		Returns:
			dict: Dictionary of node attributes.
		"""
		node_properties.update({'border-width': border_width})
		return node_properties

	@staticmethod
	def set_node_border_style_property(node_properties, border_style):
		"""Set the border width in node_properties.

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			border_style (str): Style of border.

		Returns:
			dict: Dictionary of node attributes.

		Raises:
			Exception: If the border_style parameter is not one of the allowed border styles. See ALLOWED_NODE_BORDER_STYLES for more details.
		"""
		if border_style not in GSGraph.ALLOWED_NODE_BORDER_STYLES:
			raise Exception('"%s" is not an allowed node border style.' % (border_style))
		node_properties.update({'border-style': border_style})
		return node_properties

	@staticmethod
	def set_node_border_color_property(node_properties, border_color):
		"""Set the border_color in node_properties.

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			border_color (str): Hexadecimal representation of the border color (e.g., #FFFFFF) or a color name.

		Returns:
			dict: Dictionary of node attributes.

		Raises:
			Exception: If the border_color is improperly formatted.
		"""
		error = GSGraph.check_color_hex(border_color)
		if error is not None:
			raise Exception(error)
		node_properties.update({'border-color': border_color})
		return node_properties

	@staticmethod
	def set_node_vertical_alignment_property(node_properties, valign):
		"""Set the vertical alignment of label in node_properties.

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			valign (str): Vertical alignment of text.

		Returns:
			dict: Dictionary of node attributes.
		"""
		node_properties.update({'text-valign': valign})
		return node_properties

	@staticmethod
	def set_node_horizontal_alignment_property(node_properties, halign):
		"""Set the horizontal alignment of label in node_properties.

		Args:
			node_properties (dict): Dictionary of node attributes. Key-value pairs will be used to set data associated with the node.
			halign (str): Horizontal alignment of text.

		Returns:
			dict: Dictionary of node attributes.
		"""
		node_properties.update({'text-halign': halign})
		return node_properties


	####################################################################
	### EDGE PROPERTY FUNCTIONS #################################################

	@staticmethod
	def set_edge_color_property(edge_properties, color):
		"""Add a edge color to the edge_properties.

		Color both the line and the target arrow; if the edge
		is undirected, then the target arrow color doesn't matter.
		If it's directed, then the arrow color will match the line color.

		Color can be a name (e.g., 'black') or an HTML string (e.g., #00000).

		Args:
			edge_properties (dict): Dictionary of edge attributes. Key-value pairs will be used to set data associated with the edge.
			color (str): Hexadecimal representation of the color (e.g., #FFFFFF) or color name.

		Returns:
			dict: Dictionary of edge attributes.

		Raises:
			Exception: If the color is improperly formatted.
		"""
		error = GSGraph.check_color_hex(color)
		if error is not None:
			raise Exception(error)

		edge_properties.update({'line-color': color})
		edge_properties.update({'target-arrow-color': color})
		return edge_properties

	@staticmethod
	def set_edge_directionality_property(edge_properties, directed, arrow_shape='triangle'):
		"""Sets a target arrow shape.

		Args:
			edge_properties (dict): Dictionary of edge attributes. Key-value pairs will be used to set data associated with the edge.
			directed (bool): If True, draw the edge as directed.
			arrow_shape (str): Shape of arrow. Defaults to 'triangle'. See ALLOWED_ARROW_SHAPES.

		Returns:
			dict: Dictionary of edge attributes.
		"""
		if directed:
			edge_properties = GSGraph.set_edge_target_arrow_shape_property(edge_properties, arrow_shape)
		else:
			edge_properties = GSGraph.set_edge_target_arrow_shape_property(edge_properties, 'none')
		return edge_properties

	@staticmethod
	def set_edge_width_property(edge_properties, width):
		"""Sets the width property of the edge.

		Args:
			edge_properties (dict): Dictionary of edge attributes. Key-value pairs will be used to set data associated with the edge.
			width (float): Width of the edge.

		Returns:
			dict: Dictionary of edge attributes.
		"""
		edge_properties.update({'width': width})
		return edge_properties

	@staticmethod
	def set_edge_target_arrow_shape_property(edge_properties, arrow_shape):
		"""Assigns an arrow shape to edge.

		Args:
			edge_properties (dict): Dictionary of edge attributes. Key-value pairs will be used to set data associated with the edge.
			arrow_shape (str): Shape of arrow. See ALLOWED_ARROW_SHAPES.

		Returns:
			dict: Dictionary of edge attributes.
		"""
		edge_properties.update({'target-arrow-shape': arrow_shape})
		return edge_properties

	@staticmethod
	def set_edge_line_style_property(edge_properties, style):
		"""Adds the edge line style to edge.

		Args:
			edge_properties (dict): Dictionary of edge attributes. Key-value pairs will be used to set data associated with the edge.
			style (str): Style of line.

		Returns:
			dict: Dictionary of edge attributes.
		"""
		edge_properties.update({'line-style': style})
		return edge_properties

	@staticmethod
	def set_edge_target_arrow_fill(edge_properties, fill):
		"""Adds the arrowhead fill to edge.

		Args:
			edge_properties (dict): Dictionary of edge attributes. Key-value pairs will be used to set data associated with the edge.
			fill (str): Fill of arrowhead.

		Returns:
			dict: Dictionary of edge attributes.
		"""
		edge_properties.update({'target-arrow-fill': fill})
		return edge_properties

	@staticmethod
	def check_color_hex(color_code):
		"""Check the validity of the hexadecimal code of various node and edge color
		related attributes.

		This function returns an error if the hexadecimal code is not of the format
		'#XXX' or '#XXXXXX', i.e. hexadecimal color code is not valid.

		Args:
			color_code (str): Hex code of color or color name.

		Returns:
			None or str: None, if color is valid; error message if color is invalid.
		"""
		# if color name is given instead of hex code, no need to check its validity
		if not color_code.startswith('#'):
			return None
		valid = re.search(r'^#(?:[0-9a-fA-F]{1}){3,6}$', color_code)
		if valid is None:
			return color_code + ' is not a valid hex color code.'
		else:
			return None

	@staticmethod
	def validate_property(element, element_selector, property_name, valid_property_values):
		"""Goes through array to see if property is contained in the array.

		Args:
			element (dict): Element to search for in network.
			element_selector (str): Selector for element in the network.
			property_name (str): Name of the property.
			valid_property_values (List[str]): List of valid properties.

		Returns:
			None or str: None, if the property is valid or does not exist; error message if property is invalid.
		"""
		if property_name in element and element[property_name] not in valid_property_values:
			return element_selector + " contains illegal value for property: " + property_name + ".  Value given for this property was: " + \
				   element[property_name] + ".  Accepted values for property: " + property_name + " are: [" + valid_property_values + "]"

		return None

	@staticmethod
	def validate_node_data_properties(data_properties, nodes_list):
		"""Validates the data properties.

		Args:
			data_properties (dict): Dict of node data properties
			nodes_list (List[str]): List of nodes.

		Raises:
			Exception: If properties are invalid.
		"""
		# Check to see if name is in node_properties
		if "name" not in data_properties:
			raise Exception("All nodes must have a unique name.  Please verify that all nodes meet this requirement.")

		# Check the data type of node_properties, should be int, float or string
		if not (isinstance(data_properties["name"], (int, float)) or isinstance(data_properties["name"], string_types)):
			raise Exception("All nodes must be strings, integers or floats")

		if data_properties["name"] in nodes_list:
			raise Exception("There are multiple nodes with name: " + str(
				data_properties["name"]) + ".  Please make sure all node names are unique.")

	@staticmethod
	def validate_style_properties(style_properties, selector):
		"""Validates the style properties.

		Args:
			style_properties (dict): Dict of elements style properties.
			selector (str): Selector for the element.

		Returns:
			None: None, if properties are valid.

		Raises:
			Exception: If properties are invalid.

		Note:
			Refer to http://js.cytoscape.org/#selectors for selectors.
		"""
		error_list = []

		# This list contains tuple values (property_name, allowed_property_values) where property_name is the name of the property to be checked and
		# allowed_property_values is the list of allowed or legal values for that property.
		node_validity_checklist = [
			# Node specific
			("shape", GSGraph.ALLOWED_NODE_SHAPES),
			("border-style", GSGraph.ALLOWED_NODE_BORDER_STYLES),
			("background-repeat", GSGraph.ALLOWED_NODE_BACKGROUND_REPEAT),
			("text-transform", GSGraph.ALLOWED_NODE_TEXT_TRANSFORM),
			("text-wrap", GSGraph.ALLOWED_NODE_TEXT_WRAP),
			("text-background-shape", GSGraph.ALLOWED_NODE_SHAPES),
			("text-halign", GSGraph.ALLOWED_TEXT_HALIGN),
			("text-valign", GSGraph.ALLOWED_TEXT_VALIGN),
			# Edge specific
			("source-arrow-shape", GSGraph.ALLOWED_ARROW_SHAPES),
			("mid-source-arrow-shape", GSGraph.ALLOWED_ARROW_SHAPES),
			("target-arrow-shape", GSGraph.ALLOWED_ARROW_SHAPES),
			("mid-target-arrow-shape", GSGraph.ALLOWED_ARROW_SHAPES),
			("line-style", GSGraph.ALLOWED_EDGE_STYLES),
			("source-arrow-fill", GSGraph.ALLOWED_ARROW_FILL),
			("mid-source-arrow-fill", GSGraph.ALLOWED_ARROW_FILL),
			("target-arrow-fill", GSGraph.ALLOWED_ARROW_FILL),
			("mid-target-arrow-fill", GSGraph.ALLOWED_ARROW_FILL)
		]

		for property_name, allowed_property_values in node_validity_checklist:
			error = GSGraph.validate_property(style_properties, selector, property_name, allowed_property_values)
			if error is not None:
				error_list.append(error)

		# If style_properties contains a background_black property, check to make sure they have values [-1, 1]
		if "border-blacken" in style_properties and -1 <= style_properties["border-blacken"] <= 1:
			error_list.append(selector + " contains illegal border-blacken value.  Must be between [-1, 1].")

		for attr in GSGraph.NODE_COLOR_ATTRIBUTES + GSGraph.EDGE_COLOR_ATTRIBUTES:
			if attr in style_properties:
				error = GSGraph.check_color_hex(style_properties[attr])
				if error is not None:
					error_list.append(error)

		if len(error_list) > 0:
			raise Exception(", ".join(error_list))
		else:
			return None

	@staticmethod
	def validate_edge_data_properties(data_properties, nodes_list):
		"""Validates the data properties.

		Args:
			data_properties (dict): Dict of edge data properties.
			nodes_list (List[str]): List of nodes.

		Raises:
			Exception: If properties are invalid.
		"""
		# Go through all edge properties to verify if edges contain valid properties recognized by CytoscapeJS

		# If edge has no source and target nodes, throw error since they are required
		if "source" not in data_properties or "target" not in data_properties:
			raise Exception("All edges must have at least a source and target property.  Please verify that all edges meet this requirement.")

		# Check if source and target node of an edge exist in the node list
		if data_properties["source"] not in nodes_list or data_properties["target"] not in nodes_list:
			raise Exception("For all edges source and target nodes should exist in node list")

		# Check if source and target nodes are strings, integers or floats
		if not ((isinstance(data_properties["source"], (int, float)) or isinstance(data_properties["source"], string_types)) and (isinstance(data_properties["target"], (int, float)) or isinstance(data_properties["target"], string_types))):
			raise Exception("Source and target nodes of the edge must be strings, integers or floats")

		if "is_directed" not in data_properties:
			raise Exception("All edges must have a `is_directed` property.  Please verify that all edges meet this requirement.")

		# Check the data type of node_properties, should be int
		if not isinstance(data_properties["is_directed"], (int)) or (data_properties["is_directed"] > 1):
			raise Exception("All is_directed properties must be integers. Valid values are 0 or 1.")

	@staticmethod
	def validate_style_json(style_json):
		"""Validates the json representation of style of graph.

		Args:
			style_json (dict): Json representation for graph style.

		Raises:
			Exception: If properties are invalid.
		"""
		if type(style_json) is list:
			for json in style_json:
				GSGraph.validate_style_json(json)
		else:
			for elem in style_json.get('style', []):
				if 'css' in elem:
					GSGraph.validate_style_properties(elem['css'], elem['selector'])
				else:
					GSGraph.validate_style_properties(elem['style'], elem['selector'])
