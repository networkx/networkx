# -*- coding: utf-8 -*-
#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors:
#    Aric Hagberg <hagberg@lanl.gov>
#    Pieter Swart <swart@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Loïc Séguin-C. <loicseguin@gmail.com>
"""Base exceptions and errors for NetworkX."""

__all__ = [
    'HasACycle',
    'NetworkXAlgorithmError',
    'NetworkXException',
    'NetworkXError',
    'NetworkXNoCycle',
    'NetworkXNoPath',
    'NetworkXNotImplemented',
    'NetworkXPointlessConcept',
    'NetworkXUnbounded',
    'NetworkXUnfeasible',
]


class NetworkXException(Exception):
    """Base class for exceptions in NetworkX."""


class NetworkXError(NetworkXException):
    """Exception for a serious error in NetworkX"""


class NetworkXPointlessConcept(NetworkXException):
    """Raised when a null graph is provided as input to an algorithm
    that cannot use it.

    The null graph is sometimes considered a pointless concept [1]_,
    thus the name of the exception.

    References
    ----------
    .. [1] Harary, F. and Read, R. "Is the Null Graph a Pointless
       Concept?"  In Graphs and Combinatorics Conference, George
       Washington University.  New York: Springer-Verlag, 1973.

    """


class NetworkXAlgorithmError(NetworkXException):
    """Exception for unexpected termination of algorithms."""


class NetworkXUnfeasible(NetworkXAlgorithmError):
    """Exception raised by algorithms trying to solve a problem
    instance that has no feasible solution."""


class NetworkXNoPath(NetworkXUnfeasible):
    """Exception for algorithms that should return a path when running
    on graphs where such a path does not exist."""


class NetworkXNoCycle(NetworkXUnfeasible):
    """Exception for algorithms that should return a cycle when running
    on graphs where such a cycle does not exist."""


class HasACycle(NetworkXException):
    """Raised if a graph has a cycle when an algorithm expects that it
    will have no cycles.

    """


class NetworkXUnbounded(NetworkXAlgorithmError):
    """Exception raised by algorithms trying to solve a maximization
    or a minimization problem instance that is unbounded."""


class NetworkXNotImplemented(NetworkXException):
    """Exception raised by algorithms not implemented for a type of graph."""
