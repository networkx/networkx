from collections import defaultdict
from os.path import splitext
from contextlib import contextmanager
from pathlib import Path

import networkx as nx
from networkx.utils import create_random_state, create_py_random_state

import inspect, itertools, collections

import re

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


def _open_gz(path, mode):
    import gzip

    file = gzip.open(path, mode=mode)
    file._close_argmap = True
    return file


def _open_bz2(path, mode):
    import bz2

    file = bz2.BZ2File(path, mode=mode)
    file._close_argmap = True
    return file


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

    def _open_file(path):
        # Now we have the path_arg. There are two types of input to consider:
        #   1) string representing a path that should be opened
        #   2) an already opened file object
        if isinstance(path, str):
            ext = splitext(path)[1]
            fobj = _dispatch_dict[ext](path, mode=mode)
        elif hasattr(path, "read"):
            # path is already a file-like object
            fobj = path
        elif isinstance(path, Path):
            # path is a pathlib reference to a filename
            fobj = _dispatch_dict[path.suffix](str(path), mode=mode)
        else:
            # could be None, in which case the algorithm will deal with it
            fobj = path

        return fobj

    def _close_file(f):
        if hasattr(f, "_close_argmap"):
            f.close()

    map_outer = argmap.call_finally(_close_file, path_arg)
    map_inner = argmap(_open_file, path_arg)

    def decorate(f):
        return map_outer(map_inner(f))

    return decorate


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


def compile_argmap(func):
    real_func = func.__argmap_compile__()
    func.__code__ = real_func.__code__
    func.__globals__.update(real_func.__globals__)
    func.__dict__.update(real_func.__dict__)
    return func


class argmap:
    """A decorating class which calls specified functions on a function's
    arguments before calling it.  We currently support two call syntaxes.
    One is used to call a single function on multiple arguments,

    @argmap(sum, 'x', 2)
    def foo(x, y, z):
        return x, y, z

    is equivalent to

    def foo(x, y, z):
        x = sum(x)
        z = sum(z)
        return x, y, z

    The other is used to call multiple functions on multiple arguments.
    With this syntax, we can avoid quoting the parameters, but can't refer
    to them with indices.

    @argmap(x = sum, z = any)
    def foo(x, y, z):
        return (x, y, z)

    is equivalent to

    def foo(x, y, z):
        x = sum(x)
        z = any(z)
        return (x, y, z)

    This is a draft, not proper documentation, and we might only support
    one syntax in the final version.
    """

    def __init__(self, func, *args):
        self._func = func
        self._args = args
        self._finally = False

    __count = 0

    @classmethod
    def _count(self):
        """Maintain a globally-unique identifier for function names and "file" names"""
        self.__count += 1
        return self.__count

    __bad_chars = re.compile("[^a-zA-Z0-9_]")

    @classmethod
    def name(self, f):
        """Mangle the name of a function to be unique but somewhat human-readable"""
        fname = re.sub(self.__bad_chars, "_", f.__name__)
        return f"argmap_{fname}_{self._count()}"

    @classmethod
    def call_finally(cls, func, *args):
        """Alternative decorator-constructor which calls func in a finally block"""
        dec = cls(func, *args)
        dec._finally = True
        return dec

    def __call__(self, f):
        """Construct a lazily decorated wrapper of f.  The decorated function
        will be compiled when it is called for the first time, and it will
        replace its own __code__ object so subsequent calls are fast."""
        if inspect.iscoroutinefunction(f):

            async def func(*args, __wrapper=None, **kwargs):
                return await compile_argmap(__wrapper)(*args, **kwargs)

        elif inspect.isgeneratorfunction(f):

            def func(*args, __wrapper=None, **kwargs):
                yield from compile_argmap(__wrapper)(*args, **kwargs)

        else:

            def func(*args, __wrapper=None, **kwargs):
                return compile_argmap(__wrapper)(*args, **kwargs)

        func.__name__ = f.__name__
        func.__doc__ = f.__doc__
        func.__defaults__ = f.__defaults__
        func.__kwdefaults__.update(f.__kwdefaults__ or {})
        func.__module__ = f.__module__
        func.__qualname__ = f.__qualname__
        func.__dict__.update(f.__dict__)
        func.__kwdefaults__["_argmap__wrapper"] = func
        func.__argmap_assemble__ = lambda: self.assemble(f)
        func.__argmap_compile__ = lambda: self.compile(f)
        return func

    def compile(self, f):
        """Called once for a given decorated function -- collects the code from all
        argmap decorators in the stack, and compiles the decorated function."""
        body = sig, wrapped_name, functions, mapblock, finallys = self.assemble(f)

        def flatten(lines, depth=[0], tabs=" " * 512, dtab={":": 1, "#": -1}):
            tab = tabs[: depth[0]]
            for line in lines:
                if isinstance(line, list):
                    yield from flatten(line)
                else:
                    yield f"{tabs[:depth[0]]}{line}"
                    depth[0] += dtab.get(line[-1], 0)

        code = "\n".join(
            flatten(
                [
                    sig.def_sig,
                    *mapblock,
                    f"{sig.call_sig.format(wrapped_name)}#",
                    *finallys,
                ]
            )
        )

        locl = {}
        globl = dict(functions.values())
        filename = f"{self.__class__} compilation {self.__class__._count()}"
        compiled = compile(code, filename, "exec")
        exec(compiled, globl, locl)
        wrapper = locl[sig.name]
        wrapper._code = code
        return wrapper

    def assemble(self, f):
        """Collects the requisite data to compile the decorated version of f.
        Note, this is recursive, and all argmap-decorators will be flattened
        into a single function call"""
        if hasattr(f, "__argmap_assemble__"):
            sig, wrapped_name, functions, mapblock, finallys = f.__argmap_assemble__()
        else:
            sig = self.signature(f)
            wrapped_name = self.name(f)
            mapblock, trys, finallys = [], [], []
            functions = {id(f): (wrapped_name, f)}

        if id(self._func) in functions:
            fname, _ = functions[id(self._func)]
        else:
            fname, _ = functions[id(self._func)] = self.name(self._func), self._func

        def get_name(arg, first=True, applied=set()):
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
                if sig.kwargs is None:
                    raise nx.NetworkXError(
                        f"index {arg} not a parameter index and this function doesn't have args"
                    )
                return f"{sig.args}[{arg-sig.n_positional}]"

        if self._finally:
            mapblock.extend("try:" for a in self._args)
            for name in map(get_name, self._args):
                finallys = ["finally:", f"{name} = {fname}({name})#", "#", finallys]
        else:
            mapblock.extend(
                f"{name} = {fname}({name})" for name in map(get_name, self._args)
            )

        return sig, wrapped_name, functions, mapblock, finallys

    @classmethod
    def signature(cls, f):
        """compute a signature for wrapping f"""
        sig = inspect.signature(f, follow_wrapped=False)
        def_sig = []
        call_sig = []
        names = {}

        kind = None
        star = None
        kwar = None
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
                star = param.name
                count = 0
            elif kind == param.VAR_KEYWORD:
                name = "**" + param.name
                kwar = param.name
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
        coroutine = inspect.iscoroutinefunction(f)
        _async = "async " if coroutine else ""
        def_sig = f'{_async}def {fname}({", ".join(def_sig)}):'

        if coroutine:
            _return = "return await"
        elif inspect.isgeneratorfunction(f):
            _return = "yield from"
        else:
            _return = "return"

        call_sig = f"{_return} {{}}({', '.join(call_sig)})"

        return cls.Signature(fname, sig, def_sig, call_sig, names, npos, star, kwar)

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
