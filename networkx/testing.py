"""
    Some functions and decorators to aid with testing.
"""

__all__ = ['NotImplementedTest', 'requires']

### Taken from: numpy/testing/decorators.py
def skipif(skip_condition, msg=None):
    """
    Make function raise SkipTest exception if a given condition is true.

    If the condition is a callable, it is used at runtime to dynamically
    make the decision. This is useful for tests that may require costly
    imports, to delay the cost until the test suite is actually executed.

    Parameters
    ----------
    skip_condition : bool or callable
        Flag to determine whether to skip the decorated test.
    msg : str, optional
        Message to give on raising a SkipTest exception. Default is None.

    Returns
    -------
    decorator : function
        Decorator which, when applied to a function, causes SkipTest
        to be raised when `skip_condition` is True, and the function
        to be called normally otherwise.

    Notes
    -----
    The decorator itself is decorated with the ``nose.tools.make_decorator``
    function in order to transmit function name, and various other metadata.

    """

    def skip_decorator(f):
        # Local import to avoid a hard nose dependency and only incur the
        # import time overhead at actual test-time.
        import nose

        # Allow for both boolean or callable skip conditions.
        if callable(skip_condition):
            skip_val = lambda : skip_condition()
        else:
            skip_val = lambda : skip_condition

        def get_msg(func,msg=None):
            """Skip message with information about function being skipped."""
            if msg is None: 
                out = 'Test skipped due to test condition'
            else: 
                out = '\n'+msg

            return "Skipping test: %s%s" % (func.__name__,out)

        # We need to define *two* skippers because Python doesn't allow both
        # return with value and yield inside the same function.
        def skipper_func(*args, **kwargs):
            """Skipper for normal test functions."""
            if skip_val():
                raise nose.SkipTest(get_msg(f,msg))
            else:
                return f(*args, **kwargs)

        def skipper_gen(*args, **kwargs):
            """Skipper for test generators."""
            if skip_val():
                raise nose.SkipTest(get_msg(f,msg))
            else:
                for x in f(*args, **kwargs):
                    yield x

        # Choose the right skipper to use when building the actual decorator.
        if nose.util.isgenerator(f):
            skipper = skipper_gen
        else:
            skipper = skipper_func
            
        return nose.tools.make_decorator(f)(skipper)

    return skip_decorator


class ModuleImporter(object):
    """Helper class for use with numpy.testing.skipif."""

    def __init__(self, module):
        """Initializes the instance to import the `module`.

        Parameters
        ----------
        module : str
            The name of the module that should be imported.

        """
        self.module = module

    def is_missing(self):
        """Returns True if the module cannot be imported."""
        try:
            __import__(self.module)
        except ImportError:
            return True
        else:
            return False


def requires(*modules):
    """Function decorator to skip test if all dependencies do not exist.

    Parameters
    ----------
    args : list of str
        A list of module names that the test requires.
    
    Example
    -------
    
    @requires('scipy.stats')
    def statistical_test1():
        pass
        
    """
    skip_decorators = []
    # apply dependencies in reverse order so that first one is tested first.
    for module in reversed(modules):
        msg = "%s is required but not present." % (module,)
        sd = skipif(ModuleImporter(module).is_missing, msg)
        skip_decorators.append(sd)

    def requires_decorator(f):
        print "here"
        for sd in skip_decorators:
            f = sd(f)
        return f
    
    return requires_decorator
    
# A decorator to mark a test as not implemented.
msg = "Test not implemented or depends on something not implemented."
NotImplementedTest = skipif(NotImplementedError, msg)

    

