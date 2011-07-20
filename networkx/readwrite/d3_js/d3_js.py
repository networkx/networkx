#!/usr/bin/env python
# encoding: utf-8
"""
d3_js.py

Description: Read and write files in the D3.js JSON file format.  This
can be used to generate interactive Java Script embeds from NetworkX
graph objects.

These functions will read and write the D3.js JavaScript Object Notation (JSON)
format for a graph object. There is also a function to write write HTML and Javascript 
files need to render force-directed layout of graph object in a browser.  The default
redering options are based on the force-directed example by Mike Bostock at
(http://mbostock.github.com/d3/ex/force.html).

Created by Drew Conway (drew.conway@nyu.edu) on 2011-07-13 
# Copyright (c) 2011, under the Simplified BSD License.  
# For more information on FreeBSD see: http://www.opensource.org/licenses/bsd-license.php
# All rights reserved.
"""

__author__="""Drew Conway (drew.conway@nyu.edu)"""

__all__=['write_d3_js',
		 'ds_json',
		 'export_d3_js']

import os
from shutil import copyfile
from networkx.utils import _get_fh, make_str
import networkx as nx
import json
import re

def write_d3_js(G, path, group='group'):
	"""Writes a NetworkX graph in D3.js JSON graph format to disk.
	
	Parameters
	----------
	G : graph
		a NetworkX graph
	path : file or string
       File or filename to write. If a file is provided, it must be
       opened in 'wb' mode. Filenames ending in .gz or .bz2 will be compressed.
	group : string, optional
		The name 'group' key for each node in the graph. This is used to 
		assign nodes to exclusive partitions, and for node coloring if visualizing.
		
	Examples
	--------
	>>> G = nx.path_graph(4)
	>>> G.add_nodes_from(map(lambda i: (i, {'group': i}), G.nodes()))
	>>> nx.write_d3_js(G, 'four_color_line.json')
	"""
	fh = _get_fh(path, 'wb')
	graph_json = d3_json(G, group)
	graph_dump = json.dumps(graph_json, indent=2)
	fh.write(graph_dump)
	

def d3_json(G, group='group'):
	"""Converts a NetworkX Graph to a properly D3.js JSON formatted dictionary
	
	Parameters
	----------
	G : graph
		a NetworkX graph
	group : string, optional
		The name 'group' key for each node in the graph. This is used to 
		assign nodes to exclusive partitions, and for node coloring if visualizing.
		
	Examples
	--------
	>>> G = nx.path_graph(4)
	>>> G.add_nodes_from(map(lambda i: (i, {'group': i}), G.nodes()))
	>>> nx.d3_json(G)
	{'links': [{'source': 0, 'target': 1, 'value': 1},
	  {'source': 1, 'target': 2, 'value': 1},
	  {'source': 2, 'target': 3, 'value': 1}],
	 'nodes': [{'group': 0, 'nodeName': 0},
	  {'group': 1, 'nodeName': 1},
	  {'group': 2, 'nodeName': 2},
	  {'group': 3, 'nodeName': 3}]}
	"""
	ints_graph = nx.convert_node_labels_to_integers(G, discard_old_labels=False)
	graph_nodes = ints_graph.nodes(data=True)
	graph_edges = ints_graph.edges(data=True)
	
	node_labels = [(b,a) for (a,b) in ints_graph.node_labels.items()]
	node_labels.sort()
	
	# Build up node dictionary in JSON format
	node_attr = [(b) for (a,b) in graph_nodes]
	if len(node_attr[0].keys()) >1:
		raise nx.NetworkXError("Nodes in the D3.js format can only have a single attribute for 'group'.")
	elif all(map(lambda v: v.keys()[0]==group, node_attr)):	
		graph_json = {'nodes' : map(lambda n: {'name': str(node_labels[n][1]), 'group' : graph_nodes[n][1][group]}, xrange(len(node_labels)))}
	else:
		graph_json = {'nodes': map(lambda n: {'name': str(node_labels[n][1]), 'group' : 0}, xrange(len(node_labels)))}
	
	# Build up edge dictionary in JSON format
	json_edges = list()
	for j, k, w in graph_edges:
		e = {'source' : j, 'target' : k}
		if any(map(lambda k: k=='weight', w.keys())):
			e['value'] = w['weight']
		else:
			e['value'] = 1
		json_edges.append(e)
	
	graph_json['links'] = json_edges
	return graph_json
	
def export_d3_js(G, files_dir='nx_js_d3_graph', graphname="nx_js_d3_graph", group='group', width=960, height=500, node_labels=False):
	"""
	A function that exports a NetworkX graph as an interavtice D3.js object.  
	The function builds a folder, containing the graph's formatted JSON, the D3.js 
	JavaScript, and an HTML page to load the graph in a browser.
	
	Parameters
	----------
	G : graph
		a NetworkX graph
	files_dir : string, optional
		name of directory to save files
	graphname : string, optional
		the name of the graph being save as JSON, will appears in directory as 'graphname.json'
	group : string, optional
		The name of the 'group' key for each node in the graph. This is used to 
		assign nodes to exclusive partitions, and for node coloring if visualizing.
	width : int, optional
		width (px) of display frame for graph object in browser window
	height : int, optional
		height (px) of display frame for graph object in browser window
	node_labels : bool, optional
		If true, nodes are displayed with labels in browser
		
	Examples
	--------
	>>> num_nodes = 100
	>>> m = 2
	>>> G = nx.barabasi_albert_graph(num_nodes, m)
	>>> low = 0
	>>> high = 5
	>>> G.add_nodes_from(map(lambda i: (i, {'group': random.random_integers(low, high, 1)[0]}), G.nodes()))
	>>> G.add_edges_from(map(lambda e: (e[0], e[1], {'weight': random.random_integers(low+1, high, 1)[0]}), G.edges()))
	>>> export_d3_js(G, files_dir="barabasi_albert_test", graphname="random_barabasi_albert", node_labels=False)
	"""
	if not os.path.exists(files_dir):
	    os.makedirs(files_dir)
	
	write_d3_js(G, path=files_dir+"/"+graphname+".json", group=group)
	
	if not os.path.exists(files_dir+"/d3"):
		os.makedirs(files_dir+"/d3")
	
	d3_js_files = ['d3/d3.js', 'd3/d3.geom.js', 'd3/d3.layout.js', 'd3/examples/force/force.css']
	for f in d3_js_files:
		copyfile(f, files_dir+'/d3/'+f.split('/')[-1])
	
	force_js = open('d3/examples/force/force.js', "r")
	nx_force_js = open(files_dir+'/'+graphname+'.js', "w")
	for line in force_js.readlines():
		if line.find('w = 960') > 0:
			line = line.replace('w = 960', 'w = '+str(width))
		if line.find('h = 500') > 0:
			line = line.replace('h = 500', 'h = '+str(height))
		if line.find('"nx_js_d3_graph.json"') > 0:
			line = line.replace('"nx_js_d3_graph.json"', '"'+graphname+'.json"')
		nx_force_js.write(line)
		if line.find('drag') > 0 and node_labels:
			label_func = '''\n  node.append("svg:text")
    .attr("class", "nodetext")
    .attr("dx", 10)
	.attr("dy", ".35em")
	.text(function(d) { return d.name; });

  node.append("svg:title")
    .text(function(d) { return d.name; });\n'''
			nx_force_js.write(label_func)
	force_js.close()
	nx_force_js.close()
	
	force_html = open('d3/examples/force/force.html', "r")
	nx_force_html = open(files_dir+'/'+graphname+'.html', "w")
	for line in force_html.readlines():
		if line.find('"../../d3.js"') > 0:
			line = line.replace('"../../d3.js"', '"d3/d3.js"')
		if line.find('"../../d3.geom.js"') > 0:
			line = line.replace('"../../d3.geom.js"', '"d3/d3.geom.js"')
		if line.find('"../../d3.layout.js"') > 0:
			line = line.replace('"../../d3.layout.js"', '"d3/d3.layout.js"')
		if line.find('"force.css"') > 0:
			line = line.replace('"force.css"', '"d3/force.css"')
		if line.find('"force.js"') > 0:
			line = line.replace('"force.js"', '"'+graphname+'.js"')
		nx_force_html.write(line)
	force_html.close()
	nx_force_html.close()