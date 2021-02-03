"""
Miscellaneous Helpers for NetworkX.

These are not imported into the base networkx namespace but
can be accessed, for example, as

>>> import networkx
>>> networkx.utils.make_list_of_ints({1, 2, 3})
[1, 2, 3]
>>> networkx.utils.arbitrary_element({5, 1, 7})  # doctest: +SKIP
1
"""

from collections import defaultdict, deque
from collections.abc import Iterable, Iterator, Sized
import warnings
import sys
import uuid
from itertools import tee, chain
import networkx as nx


# some cookbook stuff
# used in deciding whether something is a bunch of nodes, edges, etc.
# see G.add_nodes and others in Graph Class in networkx/base.py


def is_string_like(obj):  # from John Hunter, types-free version
    """Check if obj is string.

    .. deprecated:: 2.6
        This is deprecated and will be removed in NetworkX v3.0.
    """
    msg = (
        "is_string_like is deprecated and will be removed in 3.0."
        "Use isinstance(obj, str) instead."
    )
    warnings.warn(msg, DeprecationWarning)
    return isinstance(obj, str)


def iterable(obj):
    """Return True if obj is iterable with a well-defined len().

    .. deprecated:: 2.6
        This is deprecated and will be removed in NetworkX v3.0.
    """
    msg = (
        "iterable is deprecated and will be removed in 3.0."
        "Use isinstance(obj, (collections.abc.Iterable, collections.abc.Sized)) instead."
    )
    warnings.warn(msg, DeprecationWarning)
    if hasattr(obj, "__iter__"):
        return True
    try:
        len(obj)
    except:
        return False
    return True


def empty_generator():
    """ Return a generator with no members """
    yield from ()


def flatten(obj, result=None):
    """ Return flattened version of (possibly nested) iterable object. """
    if not isinstance(obj, (Iterable, Sized)) or isinstance(obj, str):
        return obj
    if result is None:
        result = []
    for item in obj:
        if not isinstance(item, (Iterable, Sized)) or isinstance(item, str):
            result.append(item)
        else:
            flatten(item, result)
    return tuple(result)


def make_list_of_ints(sequence):
    """Return list of ints from sequence of integral numbers.

    All elements of the sequence must satisfy int(element) == element
    or a ValueError is raised. Sequence is iterated through once.

    If sequence is a list, the non-int values are replaced with ints.
    So, no new list is created
    """
    if not isinstance(sequence, list):
        result = []
        for i in sequence:
            errmsg = f"sequence is not all integers: {i}"
            try:
                ii = int(i)
            except ValueError:
                raise nx.NetworkXError(errmsg) from None
            if ii != i:
                raise nx.NetworkXError(errmsg)
            result.append(ii)
        return result
    # original sequence is a list... in-place conversion to ints
    for indx, i in enumerate(sequence):
        errmsg = f"sequence is not all integers: {i}"
        if isinstance(i, int):
            continue
        try:
            ii = int(i)
        except ValueError:
            raise nx.NetworkXError(errmsg) from None
        if ii != i:
            raise nx.NetworkXError(errmsg)
        sequence[indx] = ii
    return sequence


def is_list_of_ints(intlist):
    """Return True if list is a list of ints.

    .. deprecated:: 2.6
        This is deprecated and will be removed in NetworkX v3.0.
    """
    msg = (
        "is_list_of_ints is deprecated and will be removed in 3.0."
        "See also: ``networkx.utils.make_list_of_ints.``"
    )
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
    if not isinstance(intlist, list):
        return False
    for i in intlist:
        if not isinstance(i, int):
            return False
    return True


def make_str(x):
    """Returns the string representation of t.

    .. deprecated:: 2.6
        This is deprecated and will be removed in NetworkX v3.0.
    """
    msg = "make_str is deprecated and will be removed in 3.0. Use str instead."
    warnings.warn(msg, DeprecationWarning)
    return str(x)


def generate_unique_node():
    """Generate a unique node label.

    .. deprecated:: 2.6
        This is deprecated and will be removed in NetworkX v3.0.
    """
    msg = "generate_unique_node is deprecated and will be removed in 3.0. Use uuid.uuid4 instead."
    warnings.warn(msg, DeprecationWarning)
    return str(uuid.uuid4())


def default_opener(filename):
    """Opens `filename` using system's default program.

    Parameters
    ----------
    filename : str
        The path of the file to be opened.

    """
    from subprocess import call

    cmds = {
        "darwin": ["open"],
        "linux": ["xdg-open"],
        "linux2": ["xdg-open"],
        "win32": ["cmd.exe", "/C", "start", ""],
    }
    cmd = cmds[sys.platform] + [filename]
    call(cmd)


def dict_to_numpy_array(d, mapping=None):
    """Convert a dictionary of dictionaries to a numpy array
    with optional mapping."""
    try:
        return dict_to_numpy_array2(d, mapping)
    except (AttributeError, TypeError):
        # AttributeError is when no mapping was provided and v.keys() fails.
        # TypeError is when a mapping was provided and d[k1][k2] fails.
        return dict_to_numpy_array1(d, mapping)


def dict_to_numpy_array2(d, mapping=None):
    """Convert a dictionary of dictionaries to a 2d numpy array
    with optional mapping.

    """
    import numpy as np

    if mapping is None:
        s = set(d.keys())
        for k, v in d.items():
            s.update(v.keys())
        mapping = dict(zip(s, range(len(s))))
    n = len(mapping)
    a = np.zeros((n, n))
    for k1, i in mapping.items():
        for k2, j in mapping.items():
            try:
                a[i, j] = d[k1][k2]
            except KeyError:
                pass
    return a


def dict_to_numpy_array1(d, mapping=None):
    """Convert a dictionary of numbers to a 1d numpy array
    with optional mapping.

    """
    import numpy as np

    if mapping is None:
        s = set(d.keys())
        mapping = dict(zip(s, range(len(s))))
    n = len(mapping)
    a = np.zeros(n)
    for k1, i in mapping.items():
        i = mapping[k1]
        a[i] = d[k1]
    return a


def is_iterator(obj):
    """Returns True if and only if the given object is an iterator object.

    .. deprecated:: 2.6.0
        Deprecated in favor of ``isinstance(obj, collections.abc.Iterator)``
    """
    msg = (
        "is_iterator is deprecated and will be removed in version 3.0. "
        "Use ``isinstance(obj, collections.abc.Iterator)`` instead."
    )
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
    has_next_attr = hasattr(obj, "__next__") or hasattr(obj, "next")
    return iter(obj) is obj and has_next_attr


def arbitrary_element(iterable):
    """Returns an arbitrary element of `iterable` without removing it.

    This is most useful for "peeking" at an arbitrary element of a set,
    but can be used for any list, dictionary, etc., as well.

    Parameters
    ----------
    iterable : `abc.collections.Iterable` instance
        Any object that implements ``__iter__``, e.g. set, dict, list, tuple,
        etc.

    Returns
    -------
    The object that results from ``next(iter(iterable))``

    Raises
    ------
    ValueError
        If `iterable` is an iterator (because the current implementation of
        this function would consume an element from the iterator).

    Examples
    --------
    Arbitrary elements from common Iterable objects:

    >>> arbitrary_element([1, 2, 3])  # list
    1
    >>> arbitrary_element((1, 2, 3))  # tuple
    1
    >>> arbitrary_element({1, 2, 3})  # set
    1
    >>> d = {k: v for k, v in zip([1, 2, 3], [3, 2, 1])}
    >>> arbitrary_element(d)  # dict_keys
    1
    >>> arbitrary_element(d.values())   # dict values
    3

    `str` is also an Iterable:

    >>> arbitrary_element("hello")
    'h'

    :exc:`ValueError` is raised if `iterable` is an iterator:

    >>> iterator = iter([1, 2, 3])  # Iterator, *not* Iterable
    >>> arbitrary_element(iterator)
    Traceback (most recent call last):
        ...
    ValueError: cannot return an arbitrary item from an iterator

    Notes
    -----
    This function does not return a *random* element. If `iterable` is
    ordered, sequential calls will return the same value::

        >>> l = [1, 2, 3]
        >>> arbitrary_element(l)
        1
        >>> arbitrary_element(l)
        1

    """
    if isinstance(iterable, Iterator):
        raise ValueError("cannot return an arbitrary item from an iterator")
    # Another possible implementation is ``for x in iterable: return x``.
    return next(iter(iterable))


# Recipe from the itertools documentation.
def consume(iterator):
    """Consume the iterator entirely.

    .. deprecated:: 2.6
        This is deprecated and will be removed in NetworkX v3.0.
    """
    # Feed the entire iterator into a zero-length deque.
    msg = (
        "consume is deprecated and will be removed in version 3.0. "
        "Use ``collections.deque(iterator, maxlen=0)`` instead."
    )
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
    deque(iterator, maxlen=0)


# Recipe from the itertools documentation.
def pairwise(iterable, cyclic=False):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a, b = tee(iterable)
    first = next(b, None)
    if cyclic is True:
        return zip(a, chain(b, (first,)))
    return zip(a, b)


def groups(many_to_one):
    """Converts a many-to-one mapping into a one-to-many mapping.

    `many_to_one` must be a dictionary whose keys and values are all
    :term:`hashable`.

    The return value is a dictionary mapping values from `many_to_one`
    to sets of keys from `many_to_one` that have that value.

    Examples
    --------
    >>> from networkx.utils import groups
    >>> many_to_one = {"a": 1, "b": 1, "c": 2, "d": 3, "e": 3}
    >>> groups(many_to_one)  # doctest: +SKIP
    {1: {'a', 'b'}, 2: {'c'}, 3: {'e', 'd'}}
    """
    one_to_many = defaultdict(set)
    for v, k in many_to_one.items():
        one_to_many[k].add(v)
    return dict(one_to_many)


def to_tuple(x):
    """Converts lists to tuples.

    Examples
    --------
    >>> from networkx.utils import to_tuple
    >>> a_list = [1, 2, [1, 4]]
    >>> to_tuple(a_list)
    (1, 2, (1, 4))
    """
    if not isinstance(x, (tuple, list)):
        return x
    return tuple(map(to_tuple, x))


def create_random_state(random_state=None):
    """Returns a numpy.random.RandomState instance depending on input.

    Parameters
    ----------
    random_state : int or RandomState instance or None  optional (default=None)
        If int, return a numpy.random.RandomState instance set with seed=int.
        if numpy.random.RandomState instance, return it.
        if None or numpy.random, return the global random number generator used
        by numpy.random.
    """
    import numpy as np

    if random_state is None or random_state is np.random:
        return np.random.mtrand._rand
    if isinstance(random_state, np.random.RandomState):
        return random_state
    if isinstance(random_state, int):
        return np.random.RandomState(random_state)
    msg = (
        f"{random_state} cannot be used to generate a numpy.random.RandomState instance"
    )
    raise ValueError(msg)


class PythonRandomInterface:
    def __init__(self, rng=None):
        try:
            import numpy as np
        except ImportError:
            msg = "numpy not found, only random.random available."
            warnings.warn(msg, ImportWarning)

        if rng is None:
            self._rng = np.random.mtrand._rand
        else:
            self._rng = rng

    def random(self):
        return self._rng.random_sample()

    def uniform(self, a, b):
        return a + (b - a) * self._rng.random_sample()

    def randrange(self, a, b=None):
        return self._rng.randint(a, b)

    def choice(self, seq):
        return seq[self._rng.randint(0, len(seq))]

    def gauss(self, mu, sigma):
        return self._rng.normal(mu, sigma)

    def shuffle(self, seq):
        return self._rng.shuffle(seq)

    #    Some methods don't match API for numpy RandomState.
    #    Commented out versions are not used by NetworkX

    def sample(self, seq, k):
        return self._rng.choice(list(seq), size=(k,), replace=False)

    def randint(self, a, b):
        return self._rng.randint(a, b + 1)

    #    exponential as expovariate with 1/argument,
    def expovariate(self, scale):
        return self._rng.exponential(1 / scale)

    #    pareto as paretovariate with 1/argument,
    def paretovariate(self, shape):
        return self._rng.pareto(shape)


#    weibull as weibullvariate multiplied by beta,
#    def weibullvariate(self, alpha, beta):
#        return self._rng.weibull(alpha) * beta
#
#    def triangular(self, low, high, mode):
#        return self._rng.triangular(low, mode, high)
#
#    def choices(self, seq, weights=None, cum_weights=None, k=1):
#        return self._rng.choice(seq


def create_py_random_state(random_state=None):
    """Returns a random.Random instance depending on input.

    Parameters
    ----------
    random_state : int or random number generator or None (default=None)
        If int, return a random.Random instance set with seed=int.
        if random.Random instance, return it.
        if None or the `random` package, return the global random number
        generator used by `random`.
        if np.random package, return the global numpy random number
        generator wrapped in a PythonRandomInterface class.
        if np.random.RandomState instance, return it wrapped in
        PythonRandomInterface
        if a PythonRandomInterface instance, return it
    """
    import random

    try:
        import numpy as np

        if random_state is np.random:
            return PythonRandomInterface(np.random.mtrand._rand)
        if isinstance(random_state, np.random.RandomState):
            return PythonRandomInterface(random_state)
        if isinstance(random_state, PythonRandomInterface):
            return random_state
    except ImportError:
        pass

    if random_state is None or random_state is random:
        return random._inst
    if isinstance(random_state, random.Random):
        return random_state
    if isinstance(random_state, int):
        return random.Random(random_state)
    msg = f"{random_state} cannot be used to generate a random.Random instance"
    raise ValueError(msg)
