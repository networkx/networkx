#    Copyright (C) 2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from functools import partial,update_wrapper
import json
from networkx.readwrite.json_graph import node_link_data,node_link_graph
__author__ = """Aric Hagberg (hagberg@lanl.gov))"""
__all__ = ['dumps','loads','dump','load']

class NXJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return node_link_data(o)


class NXJSONDecoder(json.JSONDecoder):
    def decode(self, s):
        d = json.loads(s)
        return node_link_graph(d)

# modification of json functions to serialize networkx graphs
dumps = partial(json.dumps, cls=NXJSONEncoder)
update_wrapper(dumps,json.dumps)
loads = partial(json.loads, cls=NXJSONDecoder)
update_wrapper(loads,json.loads)
dump = partial(json.dump, cls=NXJSONEncoder)
update_wrapper(dump,json.dump)
load = partial(json.load, cls=NXJSONDecoder)
update_wrapper(load,json.load)
