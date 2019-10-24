import datetime
from graphspace_python.graphs.classes.gsgraph import GSGraph


class GSLayout(object):
	"""GSLayout class.

	A GSLayout stores the details of a layout that is understood by GraphSpace.

	It stores the X,Y positions of nodes of a graph in an organised json structure.

	It also stores the style attributes of the respective nodes and edges in an organised json structure.

	It holds the information about the layout such as name and sharing status.

	It provides methods to define, modify and delete the details of the layout.

	Attributes:
		name (str): Name of layout.
		is_shared (int): Sharing status of layout. Has value 0 if layout is private, 1 if layout is shared.
		style_json (dict): Json representation for layout style.
		positions_json (dict): Json representation for layout node positions.
	"""

	def __init__(self):
		"""Construct a new 'GSLayout' object.

		"""
		self.style_json = {'style': []}
		self.positions_json = {}
		self.is_shared = 0
		self.set_name('Layout ' + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))

	def json(self):
		"""Get the json representation of layout details.

		Returns:
			dict: Json representation of layout details.

		Examples:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.json()
			{'style_json': {'style': []}, 'positions_json': {}, 'name':
			'Layout 03:42PM on July 20, 2017', 'is_shared': 0}
			>>> L.set_node_position('a', y=38.5, x=67.3)
			>>> L.add_node_style('a', shape='ellipse', color='green', width=60, height=60)
			>>> L.set_name('My Sample Layout')
			>>> L.json()
			{'style_json': {'style': [{'style': {'border-color': '#000000', 'border-width': 1,
			'height': 60, 'width': 60, 'shape': 'ellipse', 'border-style': 'solid', 'text-wrap':
			'wrap', 'text-halign': 'center', 'text-valign': 'center', 'background-color': 'green'},
			'selector': 'node[name="a"]'}]}, 'positions_json': {'a': {'y': 38.5, 'x': 67.3}},
			'name': 'My Sample Layout', 'is_shared': 0}
		"""
		data = {
			'name': self.get_name(),
			'is_shared': self.get_is_shared(),
			'style_json': self.get_style_json(),
			'positions_json': self.get_positions_json()
		}
		return data

	def get_name(self):
		"""Get the name of layout.

		Returns:
			str: Name of layout.

		Examples:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.get_name()
			'Layout 03:42PM on July 20, 2017'
			>>> L.set_name('My Sample Layout')
			>>> L.get_name()
			'My Sample Layout'
		"""
		return self.name

	def set_name(self, name):
		"""Set the name of the layout.

		Args:
			name (str): Name of layout.

		Example:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.set_name('My Sample Layout')
			>>> L.get_name()
			'My Sample Layout'
		"""
		self.name = name

	def get_is_shared(self):
		"""Get sharing status of the layout.

		Returns:
			int: Sharing status of layout. Either 0 or 1.

		Examples:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.get_is_shared()
			0
			>>> L.set_is_shared(1)
			>>> L.get_is_shared()
			1
		"""
		return self.is_shared

	def set_is_shared(self, is_shared=1):
		"""Set sharing status of the layout.

		Args:
		 	is_shared (int, optional): Sharing status of layout. Defaults to 1.

		Raises:
			Exception: If 'is_shared' is neither 0 nor 1.

		Examples:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.set_is_shared() # By default takes param 'is_shared' as 1.
			>>> L.get_is_shared()
			1
			>>> L.set_is_shared(0)
			>>> L.get_is_shared()
			0
		"""
		if is_shared not in [0,1]:
			raise Exception("is_shared should have value either 0 or 1.")
		else:
			self.is_shared = is_shared

	def get_positions_json(self):
		"""Get the json representation for the layout node postitions.

		Returns:
		 	dict: Json representation of layout node postitions.

		Examples:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.get_positions_json()
			{}
			>>> L.set_node_position('a', y=38.5, x=67.3)
			>>> L.get_positions_json()
			{'a': {'y': 38.5, 'x': 67.3}}
		"""
		return self.positions_json

	def set_positions_json(self, positions_json):
		"""Set the json representation for the layout node postitions.

		Args:
			positions_json (dict): Json representation of layout node positions.

		Example:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> positions_json = {
			... 	'a': {
			... 		'y': 38.5,
			... 		'x': 67.3
			... 	},
			... 	'b': {
			... 		'y': 124,
			... 		'x': 332.2
			... 	}
			... }
			>>> L.set_positions_json(positions_json)
			>>> L.get_positions_json()
			{'a': {'y': 38.5, 'x': 67.3}, 'b': {'y': 124, 'x': 332.2}}
		"""
		self.positions_json = positions_json

	def get_node_position(self, node_name):
		"""Get the x,y position of a node.

		Args:
			node_name (str): Name of the node.

		Returns:
		 	dict or None: Dict of x,y co-ordinates of the node, if node position is defined; otherwise None.

		Example:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.set_node_position('a', y=38.5, x=67.3)
			>>> L.get_node_position('a')
			{'y': 38.5, 'x': 67.3}
		"""
		return self.positions_json.get(node_name, None)

	def set_node_position(self, node_name, y, x):
		"""Set the x,y position of a node.

		Args:
			node_name (str): Name of the node.
			y (float): y co-ordinate of node.
			x (float): x co-ordinate of node.

		Examples:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.set_node_position('a', y=38.5, x=67.3)
			>>> L.get_positions_json()
			{'a': {'y': 38.5, 'x': 67.3}}
			>>> L.set_node_position('a', y=45, x=176) # Overwrites the position of 'a'.
			>>> L.get_positions_json()
			{'a': {'y': 45, 'x': 176}}
		"""
		node_position = {
			node_name: {
				'y': y,
				'x': x
			}
		}
		self.positions_json.update(node_position)

	def remove_node_position(self, node_name):
		"""Remove the x,y position of a node.

		Args:
			node_name (str): Name of the node.

		Raises:
			Exception: If node positions are undefined.

		Example:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.set_node_position('a', y=38.5, x=67.3)
			>>> L.get_positions_json()
			{'a': {'y': 38.5, 'x': 67.3}}
			>>> L.remove_node_position('a')
			>>> L.get_positions_json()
			{}
		"""
		if node_name not in self.positions_json.keys():
			raise Exception("Positions of node '%s' is undefined." % (node_name))
		else:
			del self.positions_json[node_name]

	def get_style_json(self):
		"""Get the json representation for the layout style.

		Returns:
			dict: Json representation of layout style.

		Examples:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.get_style_json()
			{'style': []}
			>>> L.add_node_style('a', shape='ellipse', color='green', width=60, height=60)
			>>> L.get_style_json()
			{'style': [{'style': {'border-color': '#000000', 'border-width': 1, 'height': 60,
			'width': 60, 'shape': 'ellipse', 'border-style': 'solid', 'text-wrap': 'wrap',
			'text-halign': 'center', 'text-valign': 'center', 'background-color': 'green'},
			'selector': 'node[name="a"]'}]}
		"""
		return self.style_json

	def set_style_json(self, style_json):
		"""Set the json representation for the layout style.

		Args:
			style_json (dict): Json representation of layout style.

		Example:
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> style_json = {
			... 	'style': [
			... 		{
			... 			'style': {
			... 				'border-color': '#000000',
			... 				'border-width': 1,
			... 				'height': 60,
			... 				'width': 60,
			... 				'shape': 'ellipse',
			... 				'border-style': 'solid',
			... 				'text-wrap': 'wrap',
			... 				'text-halign': 'center',
			... 				'text-valign': 'center',
			... 				'background-color': 'green'
			... 			},
			... 			'selector': 'node[name="a"]'
			... 		}
			... 	]
			... }
			>>> L.set_style_json(style_json)
			>>> L.get_style_json()
			{'style': [{'style': {'border-color': '#000000', 'border-width': 1, 'height': 60,
			'width': 60, 'shape': 'ellipse', 'border-style': 'solid', 'text-wrap': 'wrap',
			'text-halign': 'center', 'text-valign': 'center', 'background-color': 'green'},
			'selector': 'node[name="a"]'}]}
		"""
		GSGraph.validate_style_json(style_json)
		self.style_json = style_json

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
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.add_node_style('a', shape='ellipse', color='red', width=90, height=90)
			>>> L.add_node_style('b', color='blue', width=90, height=90, border_color='#4f4f4f')
			>>> L.get_style_json()
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

		attr_dict.update(style_properties)

		self.set_style_json({
			'style': self.get_style_json().get('style') + [{
				'selector': selector,
				'style': attr_dict
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
			>>> from graphspace_python.graphs.classes.gslayout import GSLayout
			>>> L = GSLayout()
			>>> L.add_edge_style('a', 'b', directed=True, edge_style='dotted')
			>>> L.add_edge_style('b', 'c', arrow_shape='tee', arrow_fill='hollow')
			>>> L.get_style_json()
			{'style': [{'style': {'width': 1.0, 'line-color': '#000000', 'target-arrow-shape':
			'triangle', 'line-style': 'dotted', 'target-arrow-fill': 'filled', 'target-arrow-color':
			'#000000'}, 'selector': 'edge[source="a"][target="b"]'}, {'style': {'width': 1.0,
			'line-color': '#000000', 'target-arrow-shape': 'none', 'line-style': 'solid',
			'target-arrow-fill': 'hollow', 'target-arrow-color': '#000000'}, 'selector':
			'edge[source="b"][target="c"]'}]}
		"""
		data_properties = {}
		style_properties = {}
		data_properties.update({"source": source, "target": target})
		style_properties = GSGraph.set_edge_color_property(style_properties, color)
		style_properties = GSGraph.set_edge_width_property(style_properties, width)
		style_properties = GSGraph.set_edge_target_arrow_shape_property(style_properties, arrow_shape)
		style_properties = GSGraph.set_edge_directionality_property(style_properties, directed, arrow_shape)
		style_properties = GSGraph.set_edge_line_style_property(style_properties, edge_style)
		style_properties = GSGraph.set_edge_target_arrow_fill(style_properties, arrow_fill)

		attr_dict = attr_dict if attr_dict is not None else dict()

		selector = 'edge[source="%s"][target="%s"]' % (source, target)

		attr_dict.update(style_properties)

		self.set_style_json({
			'style': self.get_style_json().get('style') + [{
				'selector': selector,
				'style': attr_dict
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
