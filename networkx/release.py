"""Release data for NetworkX."""

name = 'networkx'
version = '0.23'
description = "A package for creating and manipulating large graphs and networks."

long_description = \
"""
NetworkX is a python package for the creation, manipulation, and
study of the structure, dynamics, and functions of complex networks.  

"""
license = 'LGPL'
authors = {'Hagberg' : ('Aric Hagberg','hagberg@lanl.gov'),
           'Schult' : ('Dan Schult','dschult@colgate.edu'),
           'Swart' : ('Pieter Swart','swart@lanl.gov')
           }
url = 'http://networkx.sourceforge.net'
platforms = ['Linux','Mac OSX','Windows XP/2000/NT']
keywords = ['Networks','Graph Theory','Mathematics']
# Get date dynamically
import time
date = time.asctime()
del time
