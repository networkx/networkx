#!/usr/bin/env python
# encoding: utf-8
"""
social_graph.py

Description: This is an example of how to interact with a restful wed-based API to build a 
			 a network from social graph data.  In this case, we will use Google's SocialGraph
			 API to build the local star-graph for a given Twitter user
			
# Copyright (c) 2011, under the Simplified BSD License.  
# For more information on FreeBSD see: http://www.opensource.org/licenses/bsd-license.php
# All rights reserved.
"""

__auhthor__= """Drew Conway (drew.conway@nyu.edu)"""
__date__ = """2011-07-12"""
__credits__ = """"""
__revision__ = ""

import networkx as nx
import urllib2
import json
import re
import warnings

def socialGraphAPI(user):
	"""Returns the raw, unparsed, JSON from a call to the Google SocialGraph API
	for a given Twitter user. """
	
	gsg_url = 'https://socialgraph.googleapis.com/lookup?q=http://twitter.com/'+user+"&edo=1&edi=1"
	gsg_raw = urllib2.urlopen(gsg_url)
	return gsg_raw.readlines()[0]

def getSocialGraph(user):
	"""
	Returns the parsed JSON text from a call to the Google SocialGraph API
	for a given Twitter user.
	"""
	
	# Get the raw JSON, and check that there was no HTTP error
	gsg_json = socialGraphAPI(user)
	while gsg_json.find("Service Unavailable. Please try again later.") > -1:
		gsg_json = socialGraphAPI(user)
	# Decode the JSON, and check that the user existed
	return json.loads(gsg_json)
	
def stripURL(twitter_url):
	"""Return the user name from a given Twitter URL"""
	return re.split('[/\.]', twitter_url)[-1]
	
def buildSocialGraph(user, twitter_only=True):
	"""Builds a NetworkX DiGraph object from a Twitter user's social graph"""
	
	gsg_data = getSocialGraph(user)
	
	nodes_out = gsg_data['nodes']['http://twitter.com/'+user]['nodes_referenced'].keys()
	nodes_in = gsg_data['nodes']['http://twitter.com/'+user]['nodes_referenced_by'].keys()
	
	# Check if any data was returned, and if not, issue warning
	null_user = False
	if len(nodes_out) < 1 and len(nodes_in) < 1:
		warnings.warn("API call returned no data, check that '"+user+"' exists.\nReturning empty graph", UserWarning)
		null_user = True
	
	# Some of the nodes returned by GSG are not Twitter, but other social network website.  
	# To build a graph from links to only Twitter pages set to True to search for only 
	# nodes with 'http://twitter.com/'. This will also remove the 'http' heading around 
	# a Twitter user.
	if twitter_only and not null_user:
		nodes_out = [(v) for (v) in nodes_out if v.find('http://twitter.com/') > -1 and v.find('/account/') < 0]
		nodes_out = map(stripURL, nodes_out)	# Strips out only the user name
		nodes_in = [(v) for (v) in nodes_in if v.find('http://twitter.com/') > -1 and v.find('/account/') < 0]
		nodes_in = map(stripURL, nodes_in)
	
	# Build the edge list and return the DiGraph
	gsg_graph = nx.DiGraph()
	if not null_user:
		# To keep node labeling consistent in each case
		if not twitter_only:
			user = 'http://twitter.com/'+user
		
		gsg_graph.add_edges_from(map(lambda i: (user, nodes_out[i]), xrange(len(nodes_out))))
		gsg_graph.add_edges_from(map(lambda i: (nodes_in[i], user), xrange(len(nodes_in))))
		
	gsg_graph.name = user
	return gsg_graph
	
def main():
	test_user = 'hmason'
	test_graph = buildSocialGraph(test_user, twitter_only=True)
	
	print nx.info(test_graph)
	
	"""
	Additional problems:
	
		1: Define node types for all data returned from the API calls; including, Twitter users, 
		   Twitter lists, non-Twitter nodes, or more.
		
		2. Write a function to generate a k-snowball search for a given seed users.  This would
		   require taking users returned from buildSocialGraph and using them as new seeds.
	"""

if __name__ == '__main__':
	main()

