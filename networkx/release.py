"""Release data for NetworkX."""

#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
__date__ = "$Date$"
__credits__ = """"""
__revision__ = "$Revision: 303 $"

name = 'networkx'
version = '0.31-svn'

description = "Python package for creating and manipulating graphs and networks"

long_description = \
"""
NetworkX is a Python package for the creation, manipulation, and
study of the structure, dynamics, and functions of complex networks.  

"""
license = 'LGPL'
authors = {'Hagberg' : ('Aric Hagberg','hagberg@lanl.gov'),
           'Schult' : ('Dan Schult','dschult@colgate.edu'),
           'Swart' : ('Pieter Swart','swart@lanl.gov')
           }
url = 'http://networkx.lanl.gov/'
download_url="http://sourceforge.net/project/showfiles.php?group_id=122233"
platforms = ['Linux','Mac OSX','Windows XP/2000/NT']
keywords = ['Networks', 'Graph Theory', 'Mathematics', 'network', 'graph', 'discrete mathematics', 'math']
# Get date dynamically
import time
date = time.asctime()
del time

