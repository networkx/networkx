#!/usr/bin/env python
"""
Load football network in GML format and compute some network statistcs.

Shows how to download GML graph in a zipped file, unpack it, and load
into a NetworkX graph.

Requires Internet connection to download the URL
http://www-personal.umich.edu/~mejn/netdata/football.zip

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2007 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from networkx import *

url="http://www-personal.umich.edu/~mejn/netdata/football.zip"

try: # Python 3.x
    import urllib.request as urllib
except ImportError: # Python 2.x
    import urllib
import io
import zipfile

sock = urllib.urlopen(url)  # open URL
s=io.BytesIO(sock.read()) # read into BytesIO "file"
sock.close()

zf = zipfile.ZipFile(s) # zipfile object
txt=zf.read('football.txt').decode() # read info file
gml=zf.read('football.gml').decode() # read gml data
# throw away bogus first line with # from mejn files
gml=gml.split('\n')[1:]
G=parse_gml(gml) # parse gml data

print(txt)
# print degree for each team - number of games
for n,d in G.degree():
    print('%s %d' % (n, d))
