"""
*********
Utilities
*********

Helpers for NetworkX.

These are not imported into the base networkx namespace but
can be accessed, for example, as

>>> import networkx
>>> networkx.utils.is_string_like('spam')
True
"""
import random
import networkx
import uuid
__author__ = '\n'.join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Dan Schult(dschult@colgate.edu)',
                        'Ben Edwards(bedwards@cs.unm.edu)'])
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

### some cookbook stuff
# used in deciding whether something is a bunch of nodes, edges, etc.
# see G.add_nodes and others in Graph Class in networkx/base.py
def is_singleton(obj):
    """Is string_like or not iterable."""
    return hasattr(obj,"capitalize") or not hasattr(obj,"__iter__")

def is_string_like(obj): # from John Hunter, types-free version
    """Check if obj is string."""
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True

 
def iterable(obj):
    """ Return True if obj is iterable with a well-defined len()."""
    if hasattr(obj,"__iter__"): return True
    try:
        len(obj)
    except:
        return False
    return True

def flatten(obj, result=None):
    """ Return flattened version of (possibly nested) iterable object. """
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

def is_list_of_ints( intlist ):
    """ Return True if list is a list of ints. """
    if not isinstance(intlist,list): return False
    for i in intlist:
        if not isinstance(i,int): return False
    return True

def _get_fh(path, mode='r'):
    """ Return a file handle for given path.

    Path can be a string or a file handle.

    Attempt to uncompress/compress files ending in '.gz' and '.bz2'.

    """
    if is_string_like(path):
        if path.endswith('.gz'):
            import gzip
            fh = gzip.open(path,mode=mode)
        elif path.endswith('.bz2'):
            import bz2
            fh = bz2.BZ2File(path,mode=mode)
        else:
            fh = open(path,mode = mode)           
    elif hasattr(path, 'read'):
        fh = path
    else:
        raise ValueError('path must be a string or file handle')
    return fh

def make_str(t):
    """Return the string representation of t."""
    if is_string_like(t): return t
    return str(t)

def cumulative_sum(numbers):
    """Yield cumulative sum of numbers.
    
    >>> import networkx.utils as utils
    >>> list(utils.cumulative_sum([1,2,3,4]))
    [1, 3, 6, 10]
    """
    csum = 0
    for n in numbers:
        csum += n
        yield csum
        


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
        print("Import error: not able to import scipy")
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
        print("Import error: not able to import scipy")
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
        print("Import error: not able to import scipy")
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
        print("Import error: not able to import scipy")
        return
    random._inst = random.Random()
    stats.seed(random.randint(1,2**30),random.randint(1,2**30))
    return stats.uniform(size=n)

def scipy_discrete_sequence(n,distribution=False):
    """
    Return sample sequence of length n from a given discrete distribution.

    distribution=histogram of values, will be normalized

    """
    try: 
        import scipy.stats as stats
    except ImportError:
        print("Import error: not able to import scipy")
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


# The same helpers for choosing random sequences from distributions
# uses Python's random module
# http://www.python.org/doc/current/lib/module-random.html

def pareto_sequence(n,exponent=1.0):
    """
    Return sample sequence of length n from a Pareto distribution.
    """
    return [random.paretovariate(exponent) for i in range(n)]


def powerlaw_sequence(n,exponent=2.0):
    """
    Return sample sequence of length n from a power law distribution.
    """
    return [random.paretovariate(exponent-1) for i in range(n)]

def zipf_rv(alpha, xmin=1, seed=None):
    r"""Return a random value chosen from the Zipf distribution.

    The return value is an integer drawn from the probability distribution
    ::math::

        p(x)=\frac{x^{-\alpha}}{\zeta(\alpha,x_{min})},

    where `\zeta(\alpha,x_{min})` is the Hurwitz zeta function.        

    Parameters
    ----------
    alpha : float 
      Exponent value of the distribution
    xmin : int
      Minimum value
    seed : int
      Seed value for random number generator

    Returns
    -------
    x : int
      Random value from Zipf distribution

    Raises
    ------
    ValueError:
      If xmin < 1 or
      If alpha <= 1

    Notes
    -----
    The rejection algorithm generates random values for a the power-law
    distribution in uniformly bounded expected time dependent on
    parameters.  See [1] for details on its operation.

    Examples
    --------
    >>> nx.zipf_rv(alpha=2, xmin=3, seed=42) # doctest: +SKIP

    References
    ----------
    ..[1] Luc Devroye, Non-Uniform Random Variate Generation, 
       Springer-Verlag, New York, 1986.
       http://cg.scs.carleton.ca/~luc/rnbookindex.html
    """
    if xmin < 1:
        raise ValueError("xmin < 1")
    if alpha <= 1:
        raise ValueError("a <= 1.0")
    if not seed is None:
        random.seed(seed)
    a1 = alpha - 1.0
    b = 2**a1
    while True:
        u = 1.0 - random.random() # u in (0,1]
        v = random.random() # v in [0,1)
        x = int(xmin*u**-(1.0/a1))
        t = (1.0+(1.0/x))**a1
        if v*x*(t-1.0)/(b-1.0) <= t/b:
            break
    return x

def zipf_sequence(n, alpha=2.0, xmin=1):
    """Return a sample sequence of length n from a Zipf distribution with
    exponent parameter alpha and minimum value xmin.

    See Also
    --------
    zipf_rv
    """
    return [ zipf_rv(alpha,xmin) for _ in range(n)]

def uniform_sequence(n):
    """
    Return sample sequence of length n from a uniform distribution.
    """
    return [ random.uniform(0,n) for i in range(n)]


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
        raise networkx.NetworkXError(
                "discrete_sequence: distribution or cdistribution missing")
        

    # get a uniform random number
    inputseq=[random.random() for i in range(n)]

    # choose from CDF
    seq=[bisect.bisect_left(cdf,s)-1 for s in inputseq]
    return seq

class UnionFind:
    """Union-find data structure.

    Each unionFind instance X maintains a family of disjoint sets of
    hashable objects, supporting the following two methods:

    - X[item] returns a name for the set containing the given item.
      Each set is named by an arbitrarily-chosen one of its members; as
      long as the set remains unchanged it will keep the same name. If
      the item is not yet part of a set in X, a new singleton set is
      created for it.

    - X.union(item1, item2, ...) merges the sets containing each item
      into a single larger set.  If any item is not yet part of a set
      in X, it is added to X as one of the members of the merged set.

      Union-find data structure. Based on Josiah Carlson's code,
      http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/215912
      with significant additional changes by D. Eppstein.
      http://www.ics.uci.edu/~eppstein/PADS/UnionFind.py

    """

    def __init__(self):
        """Create a new empty union-find structure."""
        self.weights = {}
        self.parents = {}

    def __getitem__(self, object):
        """Find and return the name of the set containing the object."""

        # check for previously unknown object
        if object not in self.parents:
            self.parents[object] = object
            self.weights[object] = 1
            return object

        # find path of objects leading to the root
        path = [object]
        root = self.parents[object]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        # compress the path and return
        for ancestor in path:
            self.parents[ancestor] = root
        return root
        
    def __iter__(self):
        """Iterate through all items ever found or unioned by this structure."""
        return iter(self.parents)

    def union(self, *objects):
        """Find the sets containing the objects and merge them all."""
        roots = [self[x] for x in objects]
        heaviest = max([(self.weights[r],r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest

def generate_unique_node():
    """ Generate a unique node label."""
    return str(uuid.uuid1())

