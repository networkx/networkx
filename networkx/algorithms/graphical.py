# -*- coding: utf-8 -*-
"""Generate graphs with a given degree sequence or expected degree sequence.
"""
#    Copyright (C) 2004-2012 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Dan Schult (dschult@colgate.edu)'
                        'Joel Miller (joel.c.miller.research@gmail.com)'
                        'Ben Edwards'])

__all__ = ['is_valid_degree_sequence',
           'is_valid_degree_sequence_erdos_gallai',
           'is_valid_degree_sequence_havel_hakimi']

def is_valid_degree_sequence(sequence, method='hh'):
    """Returns True if the sequence is a valid degree sequence.

    A degree sequence is valid if some graph can realize it.

    Parameters
    ----------
    sequence : list or iterable container
        A sequence of integer node degrees

    method : "eg" | "hh"
        The method used to validate the degree sequence.
        "eg" corresponds to the Erdős-Gallai algorithm, and
        "hh" to the Havel-Hakimi algorithm.

    Returns
    -------
    valid : bool
        True if the sequence is a valid degree sequence and False if not.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> sequence = G.degree().values()
    >>> nx.is_valid_degree_sequence(sequence)
    True

    References
    ----------
    Erdős-Gallai
        [EG1960]_, [choudum1986]_

    Havel-Hakimi
        [havel1955]_, [hakimi1962]_, [CL1996]_
    """
    if method == 'eg':
        valid = is_valid_degree_sequence_erdos_gallai(sequence)
    elif method == 'hh':
        valid = is_valid_degree_sequence_havel_hakimi(sequence)
    else:
        msg = "`method` must be 'eg' or 'hh'"
        raise nx.NetworkXException(msg)
    return valid


def is_valid_degree_sequence_havel_hakimi(sequence):
    r"""Returns True if the sequence is a valid degree sequence.

    A degree sequence is valid if some graph can realize it.
    Validation proceeds via the Havel-Hakimi algorithm.

    Worst-case run time is: `O(n^(log n))`

    Parameters
    ----------
    sequence : list or iterable container
        A sequence of integer node degrees

    Returns
    -------
    valid : bool
        True if the sequence is a valid degree sequence and False if not.

    References
    ----------
    [havel1955]_, [hakimi1962]_, [CL1996]_
    """
    s = list(sequence)  # copy to list
    # some simple tests
    if len(s) == 0:
        return True # empty sequence = empty graph
    if not nx.utils.is_list_of_ints(s):
        return False   # list of ints
    if min(s)<0:
        return False      # each int not negative
    if sum(s)%2:
        return False      # must be even

    # successively reduce degree sequence by removing node of maximum degree
    # as in Havel-Hakimi algorithm
    while s:
        s.sort()    # sort in increasing order
        if s[0]<0:
            return False  # check if removed too many from some node

        d=s.pop()             # pop largest degree
        if d==0: return True  # done! rest must be zero due to ordering

        # degree must be <= number of available nodes
        if d>len(s):   return False

        # remove edges to nodes of next higher degrees
        #s.reverse()  # to make it easy to get at higher degree nodes.
        for i in range(len(s)-1,len(s)-(d+1),-1):
            s[i]-=1

    # should never get here b/c either d==0, d>len(s) or d<0 before s=[]
    return False


def is_valid_degree_sequence_erdos_gallai(sequence):
    r"""Returns True if the sequence is a valid degree sequence.

    A degree sequence is valid if some graph can realize it.
    Validation proceeds via the Erdős-Gallai algorithm.

    Worst-case run time is: `O(n^2)`

    Parameters
    ----------
    sequence : list or iterable container
        A sequence of integer node degrees 

    Returns
    -------
    valid : bool
        True if the sequence is a valid degree sequence and False if not.

    References
    ----------
    [EG1960]_, [choudum1986]_
    """
    deg_seq = sorted(sequence,reverse=True)
    n = len(deg_seq)
    # some simple tests
    if n == 0:
        return True # empty sequence = empty graph
    if not nx.utils.is_list_of_ints(deg_seq):
        return False   # list of ints
    if min(deg_seq)<0:
        return False      # each int not negative
    if sum(deg_seq)%2:
        return False      # must be even

    sigk = [i for i in range(1, len(deg_seq)) if deg_seq[i] < deg_seq[i-1]]
    for k in sigk:
        sum_deg = sum(deg_seq[0:k])
        sum_min = k*(k-1) + sum([min([k,deg_seq[i]])
                                 for i in range(k,n)])
        if sum_deg>sum_min:
            return False
    return True
