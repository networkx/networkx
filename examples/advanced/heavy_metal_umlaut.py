#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Example using unicode strings as graph labels.  

Also shows creative use of the Heavy Metal Umlaut:
http://en.wikipedia.org/wiki/Heavy_metal_umlaut

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = ""
__credits__ = """"""
__revision__ = ""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import codecs
import networkx as NX
import pylab as P


hd=u'H\u00fcsker D\u00fc'
mh=u'Mot\u00F6rhead'
mc=u'M\u00F6tley Cr\u00fce'
st=u'Sp\u0131n\u0308al Tap'
q=u'Queensr\u00ffche'
boc=u'Blue \u00d6yster Cult'
dt=u'Deatht\u00F6ngue'

G=NX.Graph()
G.add_edge(hd,mh)
G.add_edge(mc,st)
G.add_edge(boc,mc)
G.add_edge(boc,dt)
G.add_edge(st,dt)
G.add_edge(q,st)
G.add_edge(dt,mh)
G.add_edge(st,mh)

# write in UTF-8 encoding
fh=codecs.open('edgelist.utf-8','w',encoding='utf-8')
fh.write('# -*- coding: %s -*-\n'%fh.encoding) # encoding hint for emacs
NX.write_multiline_adjlist(G,fh,delimiter='\t')

# read and store in UTF-8
fh=codecs.open('edgelist.utf-8','r',encoding='utf-8')
H=NX.read_multiline_adjlist(fh,delimiter='\t')

for n in G.nodes():
    if n not in H:
        print False

print G.nodes()

try:
    pos=NX.spring_layout(G)
    NX.draw(G,pos,font_size=16,with_labels=False)
    for p in pos: # raise text positions
        pos[p][1]+=0.07
    NX.draw_networkx_labels(G,pos)
    P.show()
except:
    pass


