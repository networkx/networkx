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
#    All rights reserved.
#    BSD license.
#

# Exception handling

# the root of all Exceptions
class NetworkXException(Exception):
    """Base class for exceptions in NetworkX."""

class NetworkXError(NetworkXException):
    """Exception for a serious error in NetworkX"""

class NetworkXPointlessConcept(NetworkXException):
    """Harary, F. and Read, R. "Is the Null Graph a Pointless Concept?" 
In Graphs and Combinatorics Conference, George Washington University.
New York: Springer-Verlag, 1973.
"""

