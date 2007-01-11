"""
Utilities for networkx package

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
__date__ = "$Date: 2005-06-15 08:30:40 -0600 (Wed, 15 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1029 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import random
import networkx

### some cookbook stuff

# used in deciding whether something is a bunch of nodes, edges, etc.
# see G.add_nodes and others in Graph Class in networkx/base.py
def is_singleton(obj):
    """ Is string_like or not iterable. """
    return hasattr(obj,"capitalize") or not hasattr(obj,"__iter__")

def is_string_like(obj): # from John Hunter, types-free version
    """Check if obj is string."""
#    if hasattr(obj, 'shape'): return False # this is a workaround
                                       # for a bug in numeric<23.1
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True

 
def iterable(obj):
    """ Return True if obj is iterable with a well-defined len()  """
    if hasattr(obj,"__iter__"): return True
    try:
        len(obj)
    except:
        return False
    return True

def flatten(obj, result=None):
    """ Return flattened version of (possibly nested) iterable obj. """
    if not iterable(obj) or is_string_like(obj):
        return obj
    if result is None:
        result = []
    for item in obj:
        if not iterable(item) or is_string_like(item):
            result.append(item)
        else:
            flatten(item, result)
    return obj.__class__(result)

def iterable_to_string(obj, sep=''):
    """
    Return string obtained by concatenating the string representation
    of each element of an iterable obj, with an optional internal string
    separator specified.
    """
    if not iterable(obj):
        return str(obj)
    return sep.join([str(i) for i in obj])

def is_list_of_ints( intlist ):
    """ Return True if list is a list of ints. """
    if not isinstance(intlist,list): return False
    for i in intlist:
        if not isinstance(i,int): return False
    return True

##def iterable(obj):
##  """ Return True if obj is iterable with a well-defined len()"""
##    try:
##      len(obj)
##    except:
##      return False
##    else:
##      return True


# some helpers for choosing random sequences from distributions
# uses scipy: www.scipy.org

def scipy_pareto_sequence(n,exponent=1.0):
    """
    Return sample sequence of length n from a Pareto distribution.

    """
    try: 
        import scipy.stats as stats
    except ImportError:
        print "Import error: not able to import scipy"
        return
    random._inst = random.Random()
    stats.seed(random.randint(1,2**30),random.randint(1,2**30))
    return stats.pareto(exponent,size=n)


def scipy_powerlaw_sequence(n,exponent=2.0):
    """
    Return sample sequence of length n from a power law distribution.

    """
    try: 
        import scipy.stats as stats
    except ImportError:
        print "Import error: not able to import scipy"
        return
    random._inst = random.Random()
    stats.seed(random.randint(1,2**30),random.randint(1,2**30))
    return stats.pareto(exponent-1,size=n)


def scipy_poisson_sequence(n,mu=1.0):
    """
    Return sample sequence of length n from a Poisson distribution.

    """
    try: 
        import scipy.stats as stats
    except ImportError:
        print "Import error: not able to import scipy"
        return
    random._inst = random.Random()
    stats.seed(random.randint(1,2**30),random.randint(1,2**30))
    return stats.poisson(mu,size=n)

def scipy_uniform_sequence(n):
    """
    Return sample sequence of length n from a uniform distribution.

    """
    try: 
        import scipy.stats as stats
    except ImportError:
        print "Import error: not able to import scipy"
        return
    random._inst = random.Random()
    stats.seed(random.randint(1,2**30),random.randint(1,2**30))
    return stats.uniform(size=n)

def scipy_discrete_sequence(n,distribution=False):
    """
    Return sample sequence of length n from a given discrete distribution

    distribution=histogram of values, will be normalized

    """
    try: 
        import scipy.stats as stats
    except ImportError:
        print "Import error: not able to import scipy"
        return
    import bisect
    if not distribution:
        return "no distribution specified"
    p=distribution
    random._inst = random.Random()

    # make CDF out of distribution to use for sample
    cdf=[]
    cdf.append(0.0)
    psum=float(sum(p))
    for i in range(0,len(p)):
        cdf.append(cdf[i]+p[i]/psum)

    # get a uniform random number
    stats.seed(random.randint(1,2**30),random.randint(1,2**30))
    inputseq=stats.uniform(size=n)

    # choose from CDF
    seq=[bisect.bisect_left(cdf,s)-1 for s in inputseq]
    return seq


# some helpers for choosing random sequences from distributions
# uses pygsl: pygsl.sourceforge.org, but not all its functionality.
# note: gsl's default number generator is the same as Python's
# (Mersenne Twister)

def gsl_pareto_sequence(n,exponent=1.0,scale=1.0,seed=None):
    """
    Return sample sequence of length n from a Pareto distribution.

    """
    try:
        import pygsl.rng
    except ImportError:
        print "Import error: not able to import pygsl"
        return
    rng=pygsl.rng.rng()
    random._inst = random.Random()
    if seed is None:
        seed=random.randint(1,2**32-1)
    rng.set(seed)

    return rng.pareto(exponent,scale,n)

def gsl_powerlaw_sequence(n,exponent=2.0,scale=1.0,seed=None):
    """
    Return sample sequence of length n from a power law distribution.

    """
    try:
        import pygsl.rng
    except ImportError:
        print "Import error: not able to import pygsl"
        return
    rng=pygsl.rng.rng()
    random._inst = random.Random()
    if seed is None:
        seed=random.randint(1,2**32-1)
    rng.set(seed)

    return rng.pareto(exponent-1,scale,n)

def gsl_poisson_sequence(n,mu=1.0,seed=None):
    """
    Return sample sequence of length n from a Poisson distribution.

    """
    try:
        import pygsl.rng
    except ImportError:
        print "Import error: not able to import pygsl"
        return
    rng=pygsl.rng.rng()
    random._inst = random.Random()
    if seed is None:
        seed=random.randint(1,2**32-1)
    rng.set(seed)

    return rng.poisson(mu,n)

def gsl_uniform_sequence(n,seed=None):
    """
    Return sample sequence of length n from a uniform distribution.

    """
    try:
        import pygsl.rng
    except ImportError:
        print "Import error: not able to import pygsl"
        return
    rng=pygsl.rng.rng()
    random._inst = random.Random()
    if seed is None:
        seed=random.randint(1,2**32-1)
    rng.set(seed)

    return rng.uniform(n)


# The same helpers for choosing random sequences from distributions
# uses Python's random module
# http://www.python.org/doc/current/lib/module-random.html

def pareto_sequence(n,exponent=1.0):
    """
    Return sample sequence of length n from a Pareto distribution.
    """
    return [random.paretovariate(exponent) for i in xrange(n)]


def powerlaw_sequence(n,exponent=2.0):
    """
    Return sample sequence of length n from a power law distribution.
    """
    return [random.paretovariate(exponent-1) for i in xrange(n)]


def uniform_sequence(n):
    """
    Return sample sequence of length n from a uniform distribution.
    """
    return [ random.uniform(0,n) for i in xrange(n)]


def cumulative_distribution(distribution):
    """Return normalized cumulative distribution from discrete distribution."""

    cdf=[]
    cdf.append(0.0)
    psum=float(sum(distribution))
    for i in range(0,len(distribution)):
        cdf.append(cdf[i]+distribution[i]/psum)
    return cdf        


def discrete_sequence(n, distribution=None, cdistribution=None):
    """
    Return sample sequence of length n from a given discrete distribution
    or discrete cumulative distribution. 

    One of the following must be specified.  

    distribution = histogram of values, will be normalized
    
    cdistribution = normalized discrete cumulative distribution

    """
    import bisect

    if cdistribution is not None:
        cdf=cdistribution
    elif distribution is not None:
        cdf=cumulative_distribution(distribution)
    else:
        raise networkx.NetworkXError, \
                  "discrete_sequence: distribution or cdistribution missing"
        

    # get a uniform random number
    inputseq=[random.random() for i in xrange(n)]

    # choose from CDF
    seq=[bisect.bisect_left(cdf,s)-1 for s in inputseq]
    return seq

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/utils.txt',package='networkx')
    return suite

if __name__ == "__main__":
    import os
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
    

