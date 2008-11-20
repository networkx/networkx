"""
**********
Exceptions
**********

Base exceptions and errors for NetworkX.
    
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

# Exception handling

# the root of all Exceptions
class NetworkXException(Exception):
    """Base class for exceptions in NetworkX."""

class NetworkXError(NetworkXException):
    """Exception for a serious error in NetworkX"""

