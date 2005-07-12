"""
Utilities for NX package

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

### some cookbook stuff

# used in deciding whether something is a bunch of nodes, edges, etc.
# see G.add_nodes and others in Graph Class in NX/base.py
def is_singleton(obj):
    """ Is string_like or not iterable. """
    return hasattr(obj,"capitalize") or not hasattr(obj,"__iter__")

def is_string_like(obj): # from John Hunter, types-free version
    """Check if obj is string."""
    if hasattr(obj, 'shape'): return False # this is a workaround
                                       # for a bug in numeric<23.1
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True

 
def iterable(obj):
    """ Return True if obj is iterable with a well-defined len()  """
    try:
      len(obj)
    except: return False
    return True


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

def scipy_pareto_sequence(n,**kwds):
    """
    Return sample sequence of length n from a Pareto distribution.

    """
    try: 
        import scipy.stats as stats
    except ImportError:
        print "Import error: not able to import scipy"
        return
    random._inst = random.Random()
    exponent=kwds.get("exponent",1.0)
    stats.seed(random.randint(1,2**30),random.randint(1,2**30))
    return stats.pareto(exponent,size=n)


def scipy_powerlaw_sequence(n,**kwds):
    """
    Return sample sequence of length n from a power law distribution.

    """
    try: 
        import scipy.stats as stats
    except ImportError:
        print "Import error: not able to import scipy"
        return
    random._inst = random.Random()
    exponent=kwds.get("exponent",2.0)
    stats.seed(random.randint(1,2**30),random.randint(1,2**30))
    return stats.pareto(exponent-1,size=n)


def scipy_poisson_sequence(n,**kwds):
    """
    Return sample sequence of length n from a Poisson distribution.

    """
    try: 
        import scipy.stats as stats
    except ImportError:
        print "Import error: not able to import scipy"
        return
    random._inst = random.Random()
    mu=kwds.get("mu",1.0)
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

def scipy_discrete_sequence(n,**kwds):
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
    random._inst = random.Random()
    p=kwds.get("distribution",False)
    if p is False:
        return "no distribution specified"

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

def gsl_pareto_sequence(n,**kwds):
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
    seed=kwds.get("seed",random.randint(1,2**32-1))
    rng.set(seed)

    exponent=kwds.get("exponent",1.0)
    scale=kwds.get("scale",1.0)
    return rng.pareto(exponent,scale,n)

def gsl_powerlaw_sequence(n,**kwds):
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
    seed=kwds.get("seed",random.randint(1,2**32-1))
    rng.set(seed)

    exponent=kwds.get("exponent",2.0)
    scale=kwds.get("scale",1.0)
    return rng.pareto(exponent-1,scale,n)

def gsl_poisson_sequence(n,**kwds):
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
    seed=kwds.get("seed",random.randint(1,2**32-1))
    rng.set(seed)

    mu=kwds.get("mu",1.0)
    return rng.poisson(mu,n)

def gsl_uniform_sequence(n,**kwds):
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
    seed=kwds.get("seed",random.randint(1,2**32-1))
    rng.set(seed)

    return rng.uniform(n)


# The same helpers for choosing random sequences from distributions
# uses Python's random module
# http://www.python.org/doc/current/lib/module-random.html

def pareto_sequence(n,**kwds):
    """
    Return sample sequence of length n from a Pareto distribution.
    """
    exponent=kwds.get("exponent",1.0)
    return [random.paretovariate(exponent) for i in xrange(n)]


def powerlaw_sequence(n,**kwds):
    """
    Return sample sequence of length n from a power law distribution.
    """
    exponent=kwds.get("exponent",2.0)
    return [random.paretovariate(exponent-1) for i in xrange(n)]


def uniform_sequence(n):
    """
    Return sample sequence of length n from a uniform distribution.
    """
    return [ random.uniform(0,n) for i in xrange(n)]

def discrete_sequence(n,**kwds):
    """
    Return sample sequence of length n from a given discrete distribution

    distribution=histogram of values, will be normalized
    """
    import bisect
    p=kwds.get("distribution",False)
    if p is False:
        return "no distribution specified"

    # make CDF out of distribution to use for sample
    cdf=[]
    cdf.append(0.0)
    psum=float(sum(p))
    for i in range(0,len(p)):
        cdf.append(cdf[i]+p[i]/psum)

    # get a uniform random number
    inputseq=[random.random() for i in xrange(n)]

    # choose from CDF
    seq=[bisect.bisect_left(cdf,s)-1 for s in inputseq]
    return seq

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/utils.txt',package='NX')
    return suite

if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    

