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
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

try:
    import pyparsing
except ImportError:
    raise "pyparsing not found: install http://pyparsing.wikispaces.com/"
    
from networkx import *

url="http://www-personal.umich.edu/~mejn/netdata/polblogs.zip"

import urllib                                       
import StringIO
import zipfile

sock = urllib.urlopen(url)  # open URL
s=StringIO.StringIO(sock.read()) # read into StringIO "file"
sock.close()                                        

zf = zipfile.ZipFile(s) # zipfile object
txt=zf.read('football.txt') # read info file
gml=zf.read('football.gml') # read gml data
G=parse_gml(gml) # parse gml data

print txt
# print degree for each team - number of games
for n,d in G.degree(with_labels=True).items():
    print n,d
