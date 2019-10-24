import json
from datetime import datetime
from graphspace_python.graphs.classes.gsgraph import GSGraph


class CyJSFormat:
	@staticmethod
	def create_gsgraph(json_string):
		"""

		Parameters
		----------
		json_string: json_string to be converted to GSGraph type.

		Returns
		-------
		object: GSGraph

		Notes
		-------
		"""
		graph_json = CyJSFormat.clean_graph_json(CyJSFormat.validate_json(json_string))
		G = GSGraph()
		G.set_graph_json(graph_json)
		return G

	@staticmethod
	def clean_graph_json(original_json_string):
		"""
			Converts original_json_string in CyJS format such that its compatible with Graphspace's json format.

			Changes to node attributes:
				1. It will copy id value to the name attribute, even if the name attribute is provided by the user.
				2. If label is used in data attributes, it will copy label value to content attribute in style attributes.
				3. If content is missing, it will add default value of name of the node
				4. Convert all shape values to lower case.
				5. Convert shape value to default value of ellipse, if a wrong value is given.
			Changes to edge attributes:
				1. Add name attributes to edge data attributes.
				2. Add default target-arrow-shape value of none if not given by the user.
			Changes to graph attributes/metadata:
				1. If no name is provided change the name to "graph_{{current timestamp}}"

		"""

		# parse old json data
		old_json = json.loads(original_json_string)

		if 'nodes' in old_json['elements'] and 'edges' in old_json['elements']:
			old_nodes = [node for node in old_json['elements']['nodes']]
			old_edges = [edge for edge in old_json['elements']['edges']]
		else:
			raise Exception("JSON of graph must have 'nodes' and 'edges' property")

		new_nodes, new_edges = [], []

		# format node and edge data
		for node in old_nodes:
			if 'data' not in node:
				node['data'] = dict()

			# we do not use user provided id's anymore. if name is not provided we use ids for name.
			if 'id' in node['data']:
				node['data']['name'] = node['data']['id']

			if 'label' not in node['data']:
				node['data']['label'] = ""

			new_nodes.append(node)

		edge_names = []
		for edge in old_edges:
			if 'data' not in edge:
				edge['data'] = dict()

			# Assignes names to the edges to be the names of the nodes that they are attached to.
			# To make sure int and floats are also accepted as source and target nodes of an edge
			source_node = str(edge['data']['source']) if "source" in edge['data'] else ""
			target_node = str(edge['data']['target']) if "target" in edge['data'] else ""
			edge['data']['name'] = source_node + '-' + target_node

			# If the ID has not yet been seen (is unique), simply store the ID
			# of that edge as source-target
			if edge['data']['name'] not in edge_names:
				edge_names.append(edge['data']['name'])
			else:
				# Otherwise if there are multiple edges with the same ID,
				# append a number to the end of the ID so we can distinguish
				# multiple edges having the same source and target.
				# This needs to be done because HTML DOM needs unique IDs.
				counter = 0
				while edge['data']['name'] in edge_names:
					counter += 1
					edge['data']['name'] = edge['data']['name'] + str(counter)
				edge_names.append(edge['data']['name'])

			if "is_directed" not in edge:
				edge['is_directed'] = 0
			else:
				edge['is_directed'] = 1

			new_edges.append(edge)

		if 'data' not in old_json:
			old_json['data'] = dict()

		# If name is not provided, name is data
		if 'name' not in old_json['data']:
			old_json['data']['name'] = "graph_" + str(datetime.now())

		# build the new json
		new_json = dict()
		new_json['data'] = old_json['data']
		new_json['elements'] = {}
		new_json['elements']['nodes'] = new_nodes
		new_json['elements']['edges'] = new_edges

		return new_json

	@staticmethod
	def validate_json(original_json_string):
		"""
		Validates JSON string to see if all required properties for a GraphSpace Graph are provided.
		Cleans the JSON string to the format required for GraphSpace.

		@param original_json_string: JSON string representation of the graph
		"""

		cleaned_json = json.loads(original_json_string)

		if "elements" not in cleaned_json:
			raise Exception("JSON of graph must have 'elements' property")

		if "nodes" not in cleaned_json["elements"]:
			raise Exception("JSON of graph must have 'nodes' property")

		if not isinstance(cleaned_json["elements"]["nodes"], list):
			raise Exception("Nodes property must contain an array")

		if "edges" not in cleaned_json["elements"]:
			raise Exception("JSON of graph must have 'edges' property")

		if not isinstance(cleaned_json["elements"]["edges"], list):
			raise Exception("Edges property must contain an array")

		return json.dumps(cleaned_json)