from collections import defaultdict
from os.path import splitext
from contextlib import contextmanager
from pathlib import Path
import warnings

import networkx as nx
from decorator import decorator
from networkx.utils import create_random_state, create_py_random_state

__all__ = [
    "not_implemented_for",
    "open_file",
    "nodes_or_number",
    "preserve_random_state",
    "random_state",
    "np_random_state",
    "py_random_state",
]


def not_implemented_for(*graph_types):
    """Decorator to mark algorithms as not implemented

    Parameters
    ----------
    graph_types : container of strings
        Entries must be one of 'directed','undirected', 'multigraph', 'graph'.

    Returns
    -------
    _require : function
        The decorated function.

    Raises
    ------
    NetworkXNotImplemented
    If any of the packages cannot be imported

    Notes
    -----
    Multiple types are joined logically with "and".
    For "or" use multiple @not_implemented_for() lines.

    Examples
    --------
    Decorate functions like this::

       @not_implemented_for('directed')
       def sp_function(G):
           pass

       @not_implemented_for('directed','multigraph')
       def sp_np_function(G):
           pass
    """

    @decorator
    def _not_implemented_for(not_implement_for_func, *args, **kwargs):
        graph = args[0]
        terms = {
            "directed": graph.is_directed(),
            "undirected": not graph.is_directed(),
            "multigraph": graph.is_multigraph(),
            "graph": not graph.is_multigraph(),
        }
        match = True
        try:
            for t in graph_types:
                match = match and terms[t]
        except KeyError as e:
            raise KeyError(
                "use one or more of " "directed, undirected, multigraph, graph"
            ) from e
        if match:
            msg = f"not implemented for {' '.join(graph_types)} type"
            raise nx.NetworkXNotImplemented(msg)
        else:
            return not_implement_for_func(*args, **kwargs)

    return _not_implemented_for


def _open_gz(path, mode):
    import gzip

    return gzip.open(path, mode=mode)


def _open_bz2(path, mode):
    import bz2

    return bz2.BZ2File(path, mode=mode)


# To handle new extensions, define a function accepting a `path` and `mode`.
# Then add the extension to _dispatch_dict.
_dispatch_dict = defaultdict(lambda: open)
_dispatch_dict[".gz"] = _open_gz
_dispatch_dict[".bz2"] = _open_bz2
_dispatch_dict[".gzip"] = _open_gz


def open_file(path_arg, mode="r"):
    """Decorator to ensure clean opening and closing of files.

    Parameters
    ----------
    path_arg : int
        Location of the path argument in args.  Even if the argument is a
        named positional argument (with a default value), you must specify its
        index as a positional argument.
    mode : str
        String for opening mode.

    Returns
    -------
    _open_file : function
        Function which cleanly executes the io.

    Examples
    --------
    Decorate functions like this::

       @open_file(0,'r')
       def read_function(pathname):
           pass

       @open_file(1,'w')
       def write_function(G,pathname):
           pass

       @open_file(1,'w')
       def write_function(G, pathname='graph.dot')
           pass

       @open_file('path', 'w+')
       def another_function(arg, **kwargs):
           path = kwargs['path']
           pass
    """
    # Note that this decorator solves the problem when a path argument is
    # specified as a string, but it does not handle the situation when the
    # function wants to accept a default of None (and then handle it).
    # Here is an example:
    #
    # @open_file('path')
    # def some_function(arg1, arg2, path=None):
    #    if path is None:
    #        fobj = tempfile.NamedTemporaryFile(delete=False)
    #        close_fobj = True
    #    else:
    #        # `path` could have been a string or file object or something
    #        # similar. In any event, the decorator has given us a file object
    #        # and it will close it for us, if it should.
    #        fobj = path
    #        close_fobj = False
    #
    #    try:
    #        fobj.write('blah')
    #    finally:
    #        if close_fobj:
    #            fobj.close()
    #
    # Normally, we'd want to use "with" to ensure that fobj gets closed.
    # However, recall that the decorator will make `path` a file object for
    # us, and using "with" would undesirably close that file object. Instead,
    # you use a try block, as shown above. When we exit the function, fobj will
    # be closed, if it should be, by the decorator.

    @decorator
    def _open_file(func_to_be_decorated, *args, **kwargs):

        # Note that since we have used @decorator, *args, and **kwargs have
        # already been resolved to match the function signature of func. This
        # means default values have been propagated. For example,  the function
        # func(x, y, a=1, b=2, **kwargs) if called as func(0,1,b=5,c=10) would
        # have args=(0,1,1,5) and kwargs={'c':10}.

        # First we parse the arguments of the decorator. The path_arg could
        # be an positional argument or a keyword argument.  Even if it is
        try:
            # path_arg is a required positional argument
            # This works precisely because we are using @decorator
            path = args[path_arg]
        except TypeError:
            # path_arg is a keyword argument. It is "required" in the sense
            # that it must exist, according to the decorator specification,
            # It can exist in `kwargs` by a developer specified default value
            # or it could have been explicitly set by the user.
            try:
                path = kwargs[path_arg]
            except KeyError as e:
                # Could not find the keyword. Thus, no default was specified
                # in the function signature and the user did not provide it.
                msg = f"Missing required keyword argument: {path_arg}"
                raise nx.NetworkXError(msg) from e
            else:
                is_kwarg = True
        except IndexError as e:
            # A "required" argument was missing. This can only happen if
            # the decorator of the function was incorrectly specified.
            # So this probably is not a user error, but a developer error.
            msg = "path_arg of open_file decorator is incorrect"
            raise nx.NetworkXError(msg) from e
        else:
            is_kwarg = False

        # Now we have the path_arg. There are two types of input to consider:
        #   1) string representing a path that should be opened
        #   2) an already opened file object
        if isinstance(path, str):
            ext = splitext(path)[1]
            fobj = _dispatch_dict[ext](path, mode=mode)
            close_fobj = True
        elif hasattr(path, "read"):
            # path is already a file-like object
            fobj = path
            close_fobj = False
        elif isinstance(path, Path):
            # path is a pathlib reference to a filename
            fobj = _dispatch_dict[path.suffix](str(path), mode=mode)
            close_fobj = True
        else:
            # could be None, in which case the algorithm will deal with it
            fobj = path
            close_fobj = False

        # Insert file object into args or kwargs.
        if is_kwarg:
            new_args = args
            kwargs[path_arg] = fobj
        else:
            # args is a tuple, so we must convert to list before modifying it.
            new_args = list(args)
            new_args[path_arg] = fobj

        # Finally, we call the original function, making sure to close the fobj
        try:
            result = func_to_be_decorated(*new_args, **kwargs)
        finally:
            if close_fobj:
                fobj.close()

        return result

    return _open_file


def nodes_or_number(which_args):
    """Decorator to allow number of nodes or container of nodes.

    Parameters
    ----------
    which_args : int or sequence of ints
        Location of the node arguments in args. Even if the argument is a
        named positional argument (with a default value), you must specify its
        index as a positional argument.
        If more than one node argument is allowed, can be a list of locations.

    Returns
    -------
    _nodes_or_numbers : function
        Function which replaces int args with ranges.

    Examples
    --------
    Decorate functions like this::

       @nodes_or_number(0)
       def empty_graph(nodes):
           pass

       @nodes_or_number([0,1])
       def grid_2d_graph(m1, m2, periodic=False):
           pass

       @nodes_or_number(1)
       def full_rary_tree(r, n)
           # r is a number. n can be a number of a list of nodes
           pass
    """

    @decorator
    def _nodes_or_number(func_to_be_decorated, *args, **kw):
        # form tuple of arg positions to be converted.
        try:
            iter_wa = iter(which_args)
        except TypeError:
            iter_wa = (which_args,)
        # change each argument in turn
        new_args = list(args)
        for i in iter_wa:
            n = args[i]
            try:
                nodes = list(range(n))
            except TypeError:
                nodes = tuple(n)
            else:
                if n < 0:
                    msg = "Negative number of nodes not valid: {n}"
                    raise nx.NetworkXError(msg)
            new_args[i] = (n, nodes)
        return func_to_be_decorated(*new_args, **kw)

    return _nodes_or_number


def preserve_random_state(func):
    """Decorator to preserve the numpy.random state during a function.

    Parameters
    ----------
    func : function
        function around which to preserve the random state.

    Returns
    -------
    wrapper : function
        Function which wraps the input function by saving the state before
        calling the function and restoring the function afterward.

    Examples
    --------
    Decorate functions like this::

        @preserve_random_state
        def do_random_stuff(x, y):
            return x + y * numpy.random.random()

    Notes
    -----
    If numpy.random is not importable, the state is not saved or restored.
    """
    msg = "preserve_random_state is deprecated and will be removed in 3.0."
    warnings.warn(msg, DeprecationWarning)

    try:
        import numpy as np

        @contextmanager
        def save_random_state():
            state = np.random.get_state()
            try:
                yield
            finally:
                np.random.set_state(state)

        def wrapper(*args, **kwargs):
            with save_random_state():
                np.random.seed(1234567890)
                return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        return wrapper
    except ImportError:
        return func


def random_state(random_state_index):
    """Decorator to generate a numpy.random.RandomState instance.

    Argument position `random_state_index` is processed by create_random_state.
    The result is a numpy.random.RandomState instance.

    Parameters
    ----------
    random_state_index : int
        Location of the random_state argument in args that is to be used to
        generate the numpy.random.RandomState instance. Even if the argument is
        a named positional argument (with a default value), you must specify
        its index as a positional argument.

    Returns
    -------
    _random_state : function
        Function whose random_state keyword argument is a RandomState instance.

    Examples
    --------
    Decorate functions like this::

       @np_random_state(0)
       def random_float(random_state=None):
           return random_state.rand()

       @np_random_state(1)
       def random_array(dims, random_state=1):
           return random_state.rand(*dims)

    See Also
    --------
    py_random_state
    """

    @decorator
    def _random_state(func, *args, **kwargs):
        # Parse the decorator arguments.
        try:
            random_state_arg = args[random_state_index]
        except TypeError as e:
            raise nx.NetworkXError("random_state_index must be an integer") from e
        except IndexError as e:
            raise nx.NetworkXError("random_state_index is incorrect") from e

        # Create a numpy.random.RandomState instance
        random_state = create_random_state(random_state_arg)

        # args is a tuple, so we must convert to list before modifying it.
        new_args = list(args)
        new_args[random_state_index] = random_state
        return func(*new_args, **kwargs)

    return _random_state


np_random_state = random_state


def py_random_state(random_state_index):
    """Decorator to generate a random.Random instance (or equiv).

    Argument position `random_state_index` processed by create_py_random_state.
    The result is either a random.Random instance, or numpy.random.RandomState
    instance with additional attributes to mimic basic methods of Random.

    Parameters
    ----------
    random_state_index : int
        Location of the random_state argument in args that is to be used to
        generate the numpy.random.RandomState instance. Even if the argument is
        a named positional argument (with a default value), you must specify
        its index as a positional argument.

    Returns
    -------
    _random_state : function
        Function whose random_state keyword argument is a RandomState instance.

    Examples
    --------
    Decorate functions like this::

       @py_random_state(0)
       def random_float(random_state=None):
           return random_state.rand()

       @py_random_state(1)
       def random_array(dims, random_state=1):
           return random_state.rand(*dims)

    See Also
    --------
    np_random_state
    """

    @decorator
    def _random_state(func, *args, **kwargs):
        # Parse the decorator arguments.
        try:
            random_state_arg = args[random_state_index]
        except TypeError as e:
            raise nx.NetworkXError("random_state_index must be an integer") from e
        except IndexError as e:
            raise nx.NetworkXError("random_state_index is incorrect") from e

        # Create a numpy.random.RandomState instance
        random_state = create_py_random_state(random_state_arg)

        # args is a tuple, so we must convert to list before modifying it.
        new_args = list(args)
        new_args[random_state_index] = random_state
        return func(*new_args, **kwargs)

    return _random_state
