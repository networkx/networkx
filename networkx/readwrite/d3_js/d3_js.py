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
		 'd3_json',
		 'export_d3_js']

import os
import sys
from shutil import copyfile
from networkx.utils import _get_fh, make_str
import networkx as nx
from networkx.readwrite.d3_js.d3_js_files import *
import json
import re	

def write_d3_js(G, path, group=None, encoding="utf-8"):
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
	encoding: string, optional
       Specify which encoding to use when writing file.
		
	Examples
	--------
	>>> from networkx.readwrite import d3_js
	>>> G = nx.path_graph(4)
	>>> G.add_nodes_from(map(lambda i: (i, {'group': i}), G.nodes()))
	>>> d3_js.write_d3_js(G, 'four_color_line.json')
	"""
	fh = _get_fh(path, 'wb')
	graph_json = d3_json(G, group)
	graph_dump = json.dumps(graph_json, indent=2)
	fh.write(graph_dump.encode(encoding))
	

def d3_json(G, group=None):
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
	>>> from networkx.readwrite import d3_js
	>>> G = nx.path_graph(4)
	>>> G.add_nodes_from(map(lambda i: (i, {'group': i}), G.nodes()))
	>>> d3_js.d3_json(G)
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
	if group is None:
		graph_json = {'nodes': map(lambda n: {'name': str(node_labels[n][1]), 'group' : 0}, xrange(len(node_labels)))}
	else:
		try:
			graph_json = {'nodes' : map(lambda n: {'name': str(node_labels[n][1]), 'group' : graph_nodes[n][1][group]}, xrange(len(node_labels)))}
		except KeyError:
			raise nx.NetworkXError("The graph had no node attribute for '"+group+"'")
		
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
	
def export_d3_js(G, files_dir='nx_js_d3_graph', graphname="nx_js_d3_graph", group='group', 
				width=960, height=500, node_labels=False, encoding="utf-8"):
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
	encoding: string, optional
       Specify which encoding to use when writing file.
		
	Examples
	--------
	>>> from scipy import random
	>>> from networkx.readwrite import d3_js
	>>> G = nx.random_lobster(20, .8, .8)
	>>> low = 0
	>>> high = 5
	>>> G.add_nodes_from(map(lambda i: (i, {'group': random.random_integers(low, high, 1)[0]}), G.nodes()))
	>>> G.add_edges_from(map(lambda e: (e[0], e[1], {'weight': random.random_integers(low+1, high, 1)[0]}), G.edges()))
	>>> d3_js.export_d3_js(G, files_dir="random_lobster", graphname="random_lobster_graph", node_labels=False)
	"""
	if not os.path.exists(files_dir):
	    os.makedirs(files_dir)
	
	write_d3_js(G, path=files_dir+"/"+graphname+".json", group=group, encoding=encoding)
	
	if not os.path.exists(files_dir+"/d3"):
		os.makedirs(files_dir+"/d3")
	
	# Begin by creating the necessary JS and HTML files
	
	# This part really sucks bad, someone needs to make this better.
	d3_files = {'d3.js' : d3_js, 'd3.geom.js' : d3_geom, 'd3.layout.js' : d3_layout, 'force.css' : d3_css, 'LICENSE' : d3_license}
	for f in d3_files.keys():
		f_open = open(files_dir+'/d3/'+f, "w")
		f_open.write(d3_files[f])
		f_open.close()
		
	# Next, go through and customize force.js and html to the given export
	
	graph_force_js = open(files_dir+'/'+graphname+'.js', "w")
	for line in d3_force.split('\n'):
		if line.find('w = 960') > 0:
			line = line.replace('w = 960', 'w = '+str(width))
		if line.find('h = 500') > 0:
			line = line.replace('h = 500', 'h = '+str(height))
		if line.find('"miserables.json"') > 0:
			line = line.replace('"miserables.json"', '"'+graphname+'.json"')
		graph_force_js.write(line+'\n'.encode(encoding))
		if line.find('drag') > 0 and node_labels:
			label_func = '''\n  node.append("svg:text")
    .attr("class", "nodetext")
    .attr("dx", 10)
	.attr("dy", ".35em")
	.text(function(d) { return d.name; });

  node.append("svg:title")
    .text(function(d) { return d.name; });\n'''
			graph_force_js.write(label_func.encode(encoding))
	graph_force_js.close()
	
	graph_force_html = open(files_dir+'/'+graphname+'.html', 'w')
	for line in d3_html.split("\n"):
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
		graph_force_html.write(line+'\n'.encode(encoding))
	graph_force_html.close()




