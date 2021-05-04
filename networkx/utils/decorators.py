from collections import defaultdict
from os.path import splitext
from contextlib import contextmanager
from pathlib import Path

import networkx as nx
from networkx.utils import create_random_state, create_py_random_state

import inspect, itertools, collections

import re, gzip, bz2

__all__ = [
    "not_implemented_for",
    "open_file",
    "nodes_or_number",
    "preserve_random_state",
    "random_state",
    "np_random_state",
    "py_random_state",
    "argmap",
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
    if "directed" in graph_types:
        assert (
            "undirected" not in graph_types
        ), "Function not implemented on graph AND multigraphs?"
    if "multigraph" in graph_types:
        assert (
            "graph" not in graph_types
        ), "Function not implemented on graph AND multigraphs?"
    if not set(graph_types) < {"directed", "undirected", "multigraph", "graph"}:
        raise KeyError(
            "use one or more of "
            f"directed, undirected, multigraph, graph, {graph_types}"
        )

    dval = ("directed" in graph_types) or not ("undirected" in graph_types) and None
    mval = ("multigraph" in graph_types) or not ("graph" in graph_types) and None
    errmsg = f"not implemented for {' '.join(graph_types)} type"

    def _not_implemented_for(g):
        if (mval is not None and mval == g.is_multigraph()) or (
            dval is not None and dval == g.is_directed()
        ):
            raise nx.NetworkXNotImplemented(errmsg)
        return g

    return argmap(_not_implemented_for, 0)


# To handle new extensions, define a function accepting a `path` and `mode`.
# Then add the extension to _dispatch_dict.
_dispatch_dict = defaultdict(lambda: open)
_dispatch_dict[".gz"] = gzip.open
_dispatch_dict[".bz2"] = bz2.BZ2File
_dispatch_dict[".gzip"] = gzip.open


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

    def _open_file(path):
        # Now we have the path_arg. There are two types of input to consider:
        #   1) string representing a path that should be opened
        #   2) an already opened file object
        if isinstance(path, str):
            ext = splitext(path)[1]
        elif isinstance(path, Path):
            # path is a pathlib reference to a filename
            ext = path.suffix
            path = str(path)
        else:
            # could be None, or a file handle, in which case the algorithm will deal with it
            return path, lambda: None

        fobj = _dispatch_dict[ext](path, mode=mode)
        return fobj, lambda: fobj.close()

    return argmap.try_finally(_open_file, path_arg)


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

    def _nodes_or_number(n):
        try:
            nodes = list(range(n))
        except TypeError:
            nodes = tuple(n)
        else:
            if n < 0:
                msg = "Negative number of nodes not valid: {n}"
                raise nx.NetworkXError(msg)
        return (n, nodes)

    try:
        iter_wa = iter(which_args)
    except TypeError:
        iter_wa = (which_args,)

    return argmap(_nodes_or_number, *iter_wa)


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
    return argmap(create_random_state, random_state_index)


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

    return argmap(create_py_random_state, random_state_index)


_tabs = " " * 512


class argmap:
    """A decorating class which calls specified transformations on a function's
    arguments before calling it.  Arguments can be specified either as strings,
    numerical indices, or (in the next example) tuples thereof

        @argmap(sum, 'x', 2)
        def foo(x, y, z):
            return x, y, z

    is equivalent to

        def foo(x, y, z):
            x = sum(x)
            z = sum(z)
            return x, y, z

    Transforming functions can be applied to multiple arguments, such as

        def swap(x, y):
            return y, x

        @argmap(swap, ('a', 'b')):
        def foo(a, b, c):
            return a, b, c

    is equivalent to

        def foo(a, b, c):
            a, b = swap(a, b)
            return a, b, z

    Also, transforming functions can preceed a try-finally block, if they both
    transform an argument and return a closing function:

        def open_file(fn):
            f = open(fn)
            return f, lambda: f.close()

        @argmap.try_finally(open_file, 'file')
        def foo(file):
            print(file.read())

    is equivalent to

        def foo(file):
            file, close_file = open_file(file)
            try:
                print(file.read())
            finally:
                close_file()

    """

    def __init__(self, func, *args):
        self._func = func
        self._args = args
        self._finally = False

    @classmethod
    def try_finally(cls, func, *args):
        """Alternative decorator-constructor which first transforms one or more
        arguments with func, executes the function to be decorated in a try
        block, and then calls a cleanup function in the associated finally
        block.  The cleanup function takes no arguments, and is expected to be
        the second value returned by func.  Hopefully this will be clear with a
        simple example:

            def open_close(filename):
                file = open(filename)
                return file, lambda: file.close()

            @argmap.try_finally(open_close, 0)
            def print_file(file):
                print(file.read())

        generates a decorated function

            def print_file(filename):
                file, close = open_close(filename)
                try:
                    print(file.read())
                finally:
                    close()

        """
        dec = cls(func, *args)
        dec._finally = True
        return dec

    @staticmethod
    def _lazy_compile(func):
        """Assemble and compile the source of our optimized decorator, and
        intrusively replace its code with the compiled version's."""
        real_func = func.__argmap__.compile(func.__wrapped__)
        func.__code__ = real_func.__code__
        func.__globals__.update(real_func.__globals__)
        func.__dict__.update(real_func.__dict__)
        return func

    def __call__(self, f):
        """Construct a lazily decorated wrapper of f.  The decorated function
        will be compiled when it is called for the first time, and it will
        replace its own __code__ object so subsequent calls are fast."""

        if inspect.isgeneratorfunction(f):

            def func(*args, __wrapper=None, **kwargs):
                yield from argmap._lazy_compile(__wrapper)(*args, **kwargs)

        else:

            def func(*args, __wrapper=None, **kwargs):
                return argmap._lazy_compile(__wrapper)(*args, **kwargs)

        # standard function-wrapping stuff
        func.__name__ = f.__name__
        func.__doc__ = f.__doc__
        func.__defaults__ = f.__defaults__
        func.__kwdefaults__.update(f.__kwdefaults__ or {})
        func.__module__ = f.__module__
        func.__qualname__ = f.__qualname__
        func.__dict__.update(f.__dict__)
        func.__wrapped__ = f

        # now that we've wrapped f, we may have picked up some __dict__ or
        # __kwdefaults__ items that were set by a previous argmap.  thus, we set
        # these values after those update() calls.

        # If we attempt to access func from within  itself, that happens through
        # a closure -- which trips an error when we replace func.__code__.  The
        # standard workaround for functions which can't see themselves is to use
        # a Y-combinator, as we do here.
        func.__kwdefaults__["_argmap__wrapper"] = func

        # this self-reference is here because functools.wraps preserves
        # everything in __dict__, and we don't want to mistake a non-argmap
        # wrapper for an argmap wrapper
        func.__self__ = func

        # this is used to variously call self.assemble and self.compile
        func.__argmap__ = self

        return func

    __count = 0

    @classmethod
    def _count(cls):
        """Maintain a globally-unique identifier for function names and "file" names"""
        cls.__count += 1
        return cls.__count

    _bad_chars = re.compile("[^a-zA-Z0-9_]")

    @classmethod
    def name(cls, f):
        """Mangle the name of a function to be unique but somewhat human-readable"""
        f = f.__name__ if hasattr(f, "__name__") else f
        fname = re.sub(cls._bad_chars, "_", f)
        return f"argmap_{fname}_{cls._count()}"

    def compile(self, f):
        """Called once for a given decorated function -- collects the code from all
        argmap decorators in the stack, and compiles the decorated function."""
        sig, wrapped_name, functions, mapblock, finallys, mutable_args = self.assemble(
            f
        )

        call = f"{sig.call_sig.format(wrapped_name)}#"
        mut_args = f"{sig.args} = list({sig.args})" if mutable_args else ""
        body = argmap._indent(sig.def_sig, mut_args, mapblock, call, finallys)
        code = "\n".join(body)

        locl = {}
        globl = dict(functions.values())
        filename = f"{self.__class__} compilation {self._count()}"
        compiled = compile(code, filename, "exec")
        exec(compiled, globl, locl)
        wrapper = locl[sig.name]
        wrapper._code = code
        return wrapper

    def assemble(self, f):
        """Collects the requisite data to compile the decorated version of f.
        Note, this is recursive, and all argmap-decorators will be flattened
        into a single function call"""

        # first, we check if f is already argmapped -- if that's the case,
        # build up the function recursively.
        # > mapblock is generally a list of function calls of the sort
        #     arg = func(arg)
        # in addition to some try-blocks.
        # > finallys is a recursive list of finally blocks of the sort
        #         finally:
        #             close_func_1()
        #     finally:
        #         close_func_2()
        # > functions is a dict of functions used in the scope of our decorated
        # function.  It will be used to construct globals used in compilation.
        # We make functions[id(f)] = name_of_f, f to ensure that a given
        # function is stored and named exactly once.
        if hasattr(f, "__argmap__") and f.__self__ is f:
            (
                sig,
                wrapped_name,
                functions,
                mapblock,
                finallys,
                mutable_args,
            ) = f.__argmap__.assemble(f.__wrapped__)
            functions = dict(functions)  # shallow-copy just in case
        else:
            sig = self.signature(f)
            wrapped_name = self.name(f)
            mapblock, finallys = [], []
            functions = {id(f): (wrapped_name, f)}
            mutable_args = False

        if id(self._func) in functions:
            fname, _ = functions[id(self._func)]
        else:
            fname, _ = functions[id(self._func)] = self.name(self._func), self._func

        # this is a bit complicated -- we can call functions with a variety of
        # arguments, so long as their input and output are tuples with the same
        # structure
        applied = set()

        def get_name(arg, first=True):
            if isinstance(arg, tuple):
                name = ", ".join(get_name(x, False) for x in arg)
                return name if first else f"({name})"
            if arg in applied:
                raise nx.NetworkXError(f"argument {name} is specified multiple times")
            applied.add(arg)
            if arg in sig.names:
                return sig.names[arg]
            elif isinstance(arg, str):
                if sig.kwargs is None:
                    raise nx.NetworkXError(
                        f"name {arg} is not a named parameter and this function doesn't have kwargs"
                    )
                return f"{sig.kwargs}[{arg!r}]"
            else:
                if sig.args is None:
                    raise nx.NetworkXError(
                        f"index {arg} not a parameter index and this function doesn't have args"
                    )
                mutable_args = True
                return f"{sig.args}[{arg-sig.n_positional}]"

        if self._finally:
            for a in self._args:
                name = get_name(a)
                final = self.name(name)
                mapblock.append(f"{name}, {final} = {fname}({name})")
                mapblock.append("try:")
                finallys = ["finally:", f"{final}()#", "#", finallys]
        else:
            mapblock.extend(
                f"{name} = {fname}({name})" for name in map(get_name, self._args)
            )

        return sig, wrapped_name, functions, mapblock, finallys, mutable_args

    @classmethod
    def signature(cls, f):
        """Compute a Signature so that we can write a function wrapping f with
        the same signature and call-type."""
        sig = inspect.signature(f, follow_wrapped=False)
        def_sig = []
        call_sig = []
        names = {}

        kind = None
        args = None
        kwargs = None
        npos = 0
        for i, param in enumerate(sig.parameters.values()):
            names[i] = names[param.name] = param.name

            # parameters can be position-only, keyword-or-position, keyword-only
            # in any combination, but only in the order as above.  we do edge
            # detection to add the appropriate punctuation
            prev = kind
            kind = param.kind
            if prev == param.POSITIONAL_ONLY != kind:
                # the last token was position-only, but this one isn't
                def_sig.append("/")
            if prev != param.KEYWORD_ONLY == kind != param.VAR_POSITIONAL:
                # param is the first keyword-only arg and isn't starred
                def_sig.append("*")

            # star arguments as appropriate
            if kind == param.VAR_POSITIONAL:
                name = "*" + param.name
                args = param.name
                count = 0
            elif kind == param.VAR_KEYWORD:
                name = "**" + param.name
                kwargs = param.name
                count = 0
            else:
                name = param.name
                count = 1

            # assign to keyword-only args in the function call
            if kind == param.KEYWORD_ONLY:
                call_sig.append(f"{name} = {name}")
            else:
                npos += count
                call_sig.append(name)

            def_sig.append(name)

        fname = cls.name(f)
        def_sig = f'def {fname}({", ".join(def_sig)}):'

        if inspect.isgeneratorfunction(f):
            _return = "yield from"
        else:
            _return = "return"

        call_sig = f"{_return} {{}}({', '.join(call_sig)})"

        return cls.Signature(fname, sig, def_sig, call_sig, names, npos, args, kwargs)

    Signature = collections.namedtuple(
        "Signature",
        [
            "name",
            "signature",
            "def_sig",
            "call_sig",
            "names",
            "n_positional",
            "args",
            "kwargs",
        ],
    )

    @staticmethod
    def _flatten(nestlist, visited):
        """flattens a recursive list of lists that doesn't have cyclic references"""
        for thing in nestlist:
            if visited.get(id(thing)) is None:
                visited[id(thing)] = True
            else:
                raise ValueError("A cycle was found in nestlist.  Be a tree.")
            if isinstance(thing, list):
                yield from argmap._flatten(thing, visited)
            else:
                yield thing

    _tabs = " " * 64

    @staticmethod
    def _indent(*lines):
        """indents a tree-recursive list of strings, following the rule that one
        space is added to the tab after a line that ends in a colon, and one is
        removed after a line that ends in an hashmark, for example

            ["try:", "try:", "pass#", "finally":", "pass#", "#", "finally:", "pass#"]

        renders to

            try:
             try:
              pass#
             finally:
              pass#
             #
            finally:
             pass#
        """
        depth = 0
        for line in argmap._flatten(lines, {}):
            yield f"{argmap._tabs[:depth]}{line}"
            depth += (line[-1:] == ":") - (line[-1:] == "#")
