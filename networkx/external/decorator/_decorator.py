##########################     LICENCE     ###############################
##
##   Copyright (c) 2005-2011, Michele Simionato
##   All rights reserved.
##
##   Redistributions of source code must retain the above copyright
##   notice, this list of conditions and the following disclaimer.
##   Redistributions in bytecode form must reproduce the above copyright
##   notice, this list of conditions and the following disclaimer in
##   the documentation and/or other materials provided with the
##   distribution.

##   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
##   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
##   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
##   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
##   HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
##   INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
##   BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
##   OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
##   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
##   TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
##   USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
##   DAMAGE.

"""
Decorator module, see http://pypi.python.org/pypi/decorator
for the documentation.
"""

__version__ = '3.3.2'

__all__ = ["decorator", "FunctionMaker", "partial"]

import sys, re, inspect

try:
    from functools import partial
except ImportError: # for Python version < 2.5
    class partial(object):
        "A simple replacement of functools.partial"
        def __init__(self, func, *args, **kw):
            self.func = func
            self.args = args
            self.keywords = kw
        def __call__(self, *otherargs, **otherkw):
            kw = self.keywords.copy()
            kw.update(otherkw)
            return self.func(*(self.args + otherargs), **kw)

if sys.version >= '3':
    from inspect import getfullargspec
else:
    class getfullargspec(object):
        "A quick and dirty replacement for getfullargspec for Python 2.X"
        def __init__(self, f):
            self.args, self.varargs, self.varkw, self.defaults = \
                inspect.getargspec(f)
            self.kwonlyargs = []
            self.kwonlydefaults = None
            self.annotations = getattr(f, '__annotations__', {})
        def __iter__(self):
            yield self.args
            yield self.varargs
            yield self.varkw
            yield self.defaults

DEF = re.compile('\s*def\s*([_\w][_\w\d]*)\s*\(')

# basic functionality
class FunctionMaker(object):
    """
    An object with the ability to create functions with a given signature.
    It has attributes name, doc, module, signature, defaults, dict and
    methods update and make.
    """
    def __init__(self, func=None, name=None, signature=None,
                 defaults=None, doc=None, module=None, funcdict=None):
        self.shortsignature = signature
        if func:
            # func can be a class or a callable, but not an instance method
            self.name = func.__name__
            if self.name == '<lambda>': # small hack for lambda functions
                self.name = '_lambda_'
            self.doc = func.__doc__
            self.module = func.__module__
            if inspect.isfunction(func):
                argspec = getfullargspec(func)
                for a in ('args', 'varargs', 'varkw', 'defaults', 'kwonlyargs',
                          'kwonlydefaults', 'annotations'):
                    setattr(self, a, getattr(argspec, a))
                for i, arg in enumerate(self.args):
                    setattr(self, 'arg%d' % i, arg)
                self.signature = inspect.formatargspec(
                    formatvalue=lambda val: "", *argspec)[1:-1]
                allargs = list(self.args)
                if self.varargs:
                    allargs.append('*' + self.varargs)
                if self.varkw:
                    allargs.append('**' + self.varkw)
                try:
                    self.shortsignature = ', '.join(allargs)
                except TypeError: # exotic signature, valid only in Python 2.X
                    self.shortsignature = self.signature
                self.dict = func.__dict__.copy()
        # func=None happens when decorating a caller
        if name:
            self.name = name
        if signature is not None:
            self.signature = signature
        if defaults:
            self.defaults = defaults
        if doc:
            self.doc = doc
        if module:
            self.module = module
        if funcdict:
            self.dict = funcdict
        # check existence required attributes
        assert hasattr(self, 'name')
        if not hasattr(self, 'signature'):
            raise TypeError('You are decorating a non function: %s' % func)

    def update(self, func, **kw):
        "Update the signature of func with the data in self"
        func.__name__ = self.name
        func.__doc__ = getattr(self, 'doc', None)
        func.__dict__ = getattr(self, 'dict', {})
        func.func_defaults = getattr(self, 'defaults', ())
        func.__kwdefaults__ = getattr(self, 'kwonlydefaults', None)
        callermodule = sys._getframe(3).f_globals.get('__name__', '?')
        func.__module__ = getattr(self, 'module', callermodule)
        func.__dict__.update(kw)

    def make(self, src_templ, evaldict=None, addsource=False, **attrs):
        "Make a new function from a given template and update the signature"
        src = src_templ % vars(self) # expand name and signature
        evaldict = evaldict or {}
        mo = DEF.match(src)
        if mo is None:
            raise SyntaxError('not a valid function template\n%s' % src)
        name = mo.group(1) # extract the function name
        names = set([name] + [arg.strip(' *') for arg in
                             self.shortsignature.split(',')])
        for n in names:
            if n in ('_func_', '_call_'):
                raise NameError('%s is overridden in\n%s' % (n, src))
        if not src.endswith('\n'): # add a newline just for safety
            src += '\n' # this is needed in old versions of Python
        try:
            code = compile(src, '<string>', 'single')
            # print >> sys.stderr, 'Compiling %s' % src
            exec code in evaldict
        except:
            print >> sys.stderr, 'Error in generated code:'
            print >> sys.stderr, src
            raise
        func = evaldict[name]
        if addsource:
            attrs['__source__'] = src
        self.update(func, **attrs)
        return func

    @classmethod
    def create(cls, obj, body, evaldict, defaults=None,
               doc=None, module=None, addsource=True, **attrs):
        """
        Create a function from the strings name, signature and body.
        evaldict is the evaluation dictionary. If addsource is true an attribute
        __source__ is added to the result. The attributes attrs are added,
        if any.
        """
        if isinstance(obj, str): # "name(signature)"
            name, rest = obj.strip().split('(', 1)
            signature = rest[:-1] #strip a right parens
            func = None
        else: # a function
            name = None
            signature = None
            func = obj
        self = cls(func, name, signature, defaults, doc, module)
        ibody = '\n'.join('    ' + line for line in body.splitlines())
        return self.make('def %(name)s(%(signature)s):\n' + ibody,
                        evaldict, addsource, **attrs)

def decorator(caller, func=None):
    """
    decorator(caller) converts a caller function into a decorator;
    decorator(caller, func) decorates a function using a caller.
    """
    if func is not None: # returns a decorated function
        evaldict = func.func_globals.copy()
        evaldict['_call_'] = caller
        evaldict['_func_'] = func
        return FunctionMaker.create(
            func, "return _call_(_func_, %(shortsignature)s)",
            evaldict, undecorated=func, __wrapped__=func)
    else: # returns a decorator
        if isinstance(caller, partial):
            return partial(decorator, caller)
        # otherwise assume caller is a function
        first = inspect.getargspec(caller)[0][0] # first arg
        evaldict = caller.func_globals.copy()
        evaldict['_call_'] = caller
        evaldict['decorator'] = decorator
        return FunctionMaker.create(
            '%s(%s)' % (caller.__name__, first),
            'return decorator(_call_, %s)' % first,
            evaldict, undecorated=caller, __wrapped__=caller,
            doc=caller.__doc__, module=caller.__module__)
