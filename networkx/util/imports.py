# This is from 
#
# Metadata-Version: 1.0
# Name: Importing
# Version: 1.9.2
# Summary: Import objects dynamically, lazily, "weakly", and more.
# Home-page: http://peak.telecommunity.com/DevCenter/Importing
# Author: Phillip J. Eby
# Author-email: peak@eby-sarna.com
# License: PSF or ZPL
#
# It is small so I'm including it here to not generate an extra dependency

"""Tools for doing dynamic imports"""

__all__ = [
    'importString', 'importObject', 'importSequence', 'importSuite',
    'lazyModule', 'joinPath', 'whenImported', 'getModuleHooks',
]
import __main__, sys
defaultGlobalDict = __main__.__dict__

from types import StringTypes, ModuleType
from sys import modules
try:
    from peak.util.EigenData import AlreadyRead
except ImportError:
    class AlreadyRead(Exception):pass


def importSuite(specs, globalDict=defaultGlobalDict):
    """Create a test suite from import specs"""

    from unittest import TestSuite

    return TestSuite(
        [t() for t in importSequence(specs,globalDict)]
    )

def joinPath(modname, relativePath):
    """Adjust a module name by a '/'-separated, relative or absolute path"""

    module = modname.split('.')
    for p in relativePath.split('/'):

        if p=='..':
            module.pop()
        elif not p:
            module = []
        elif p!='.':
            module.append(p)

    return '.'.join(module)

def importString(name, globalDict=defaultGlobalDict):
    """Import an item specified by a string

    Example Usage::

        attribute1 = importString('some.module:attribute1')
        attribute2 = importString('other.module:nested.attribute2')

    'importString' imports an object from a module, according to an
    import specification string: a dot-delimited path to an object
    in the Python package namespace.  For example, the string
    '"some.module.attribute"' is equivalent to the result of
    'from some.module import attribute'.

    For readability of import strings, it's sometimes helpful to use a ':' to
    separate a module name from items it contains.  It's optional, though,
    as 'importString' will convert the ':' to a '.' internally anyway."""

    if ':' in name:
        name = name.replace(':','.')

    parts = filter(None,name.split('.'))
    item = __import__(parts.pop(0), globalDict, globalDict, ['__name__'])

    # Fast path for the common case, where everything is imported already
    for attr in parts:
        try:
            item = getattr(item, attr)
        except AttributeError:
            break   # either there's an error, or something needs importing
    else:
        return item

    # We couldn't get there with just getattrs from the base import.  So now
    # we loop *backwards* trying to import longer names, then shorter, until
    # we find the longest possible name that can be handled with __import__,
    # then loop forward again with getattr.  This lets us give more meaningful
    # error messages than if we only went forwards.
    attrs = []
    exc = None

    try:
        while True:
            try:
                # Exit as soon as we find a prefix of the original `name`
                # that's an importable *module* or package
                item = __import__(name, globalDict, globalDict, ['__name__'])
                break
            except ImportError:
                if not exc:
                    # Save the first ImportError, as it's usually the most
                    # informative, especially w/Python < 2.4
                    exc = sys.exc_info()

                if '.' not in name:
                    # We've backed up all the way to the beginning, so reraise
                    # the first ImportError we got
                    raise exc[0],exc[1],exc[2]

                # Otherwise back up one position and try again
                parts = name.split('.')
                attrs.append(parts[-1])
                name = '.'.join(parts[:-1])
    finally:
        exc = None

    # Okay, the module object is now in 'item', so we can just loop forward
    # to retrieving the desired attribute.
    #
    while attrs:
        attr = attrs.pop()
        try:
            item = getattr(item,attr)
        except AttributeError:
            raise ImportError("%r has no %r attribute" % (item,attr))

    return item





def lazyModule(modname, relativePath=None):

    """Return module 'modname', but with its contents loaded "on demand"

    This function returns 'sys.modules[modname]', if present.  Otherwise
    it creates a 'LazyModule' object for the specified module, caches it
    in 'sys.modules', and returns it.

    'LazyModule' is a subclass of the standard Python module type, that
    remains empty until an attempt is made to access one of its
    attributes.  At that moment, the module is loaded into memory, and
    any hooks that were defined via 'whenImported()' are invoked.

    Note that calling 'lazyModule' with the name of a non-existent or
    unimportable module will delay the 'ImportError' until the moment
    access is attempted.  The 'ImportError' will occur every time an
    attribute access is attempted, until the problem is corrected.

    This function also takes an optional second parameter, 'relativePath',
    which will be interpreted as a '/'-separated path string relative to
    'modname'.  If a 'relativePath' is supplied, the module found by
    traversing the path will be loaded instead of 'modname'.  In the path,
    '.' refers to the current module, and '..' to the current module's
    parent.  For example::

        fooBaz = lazyModule('foo.bar','../baz')

    will return the module 'foo.baz'.  The main use of the 'relativePath'
    feature is to allow relative imports in modules that are intended for
    use with module inheritance.  Where an absolute import would be carried
    over as-is into the inheriting module, an import relative to '__name__'
    will be relative to the inheriting module, e.g.::

        something = lazyModule(__name__,'../path/to/something')

    The above code will have different results in each module that inherits
    it.

    (Note: 'relativePath' can also be an absolute path (starting with '/');
    this is mainly useful for module '__bases__' lists.)"""

    def _loadModule(module):

        oldGA = LazyModule.__getattribute__
        oldSA = LazyModule.__setattr__

        modGA = ModuleType.__getattribute__
        modSA = ModuleType.__setattr__

        LazyModule.__getattribute__ = modGA
        LazyModule.__setattr__      = modSA

        try:
            # Get Python (or supplied 'reload') to do the real import!
            _loadAndRunHooks(module)
        except:
            # Reset our state so that we can retry later
            if '__file__' not in module.__dict__:
                LazyModule.__getattribute__ = oldGA.im_func
                LazyModule.__setattr__      = oldSA.im_func
            raise
        try:
            # Convert to a real module (if under 2.2)
            module.__class__ = ModuleType
        except TypeError:
            pass    # 2.3 will fail, but no big deal


    class LazyModule(ModuleType):
        __slots__ = ()
        def __init__(self, name):
            ModuleType.__setattr__(self,'__name__',name)
            #super(LazyModule,self).__init__(name)

        def __getattribute__(self,attr):
            _loadModule(self)
            return ModuleType.__getattribute__(self,attr)

        def __setattr__(self,attr,value):
            _loadModule(self)
            return ModuleType.__setattr__(self,attr,value)

    if relativePath:
        modname = joinPath(modname, relativePath)

    if modname not in modules:
        getModuleHooks(modname) # force an empty hook list into existence
        modules[modname] = LazyModule(modname)
        if '.' in modname:
            # ensure parent module/package is in sys.modules
            # and parent.modname=module, as soon as the parent is imported

            splitpos = modname.rindex('.')
            whenImported(
                modname[:splitpos],
                lambda m: setattr(m,modname[splitpos+1:],modules[modname])
            )

    return modules[modname]


postLoadHooks = {}


def _loadAndRunHooks(module):

    """Load an unactivated "lazy" module object"""

    # if this fails, we haven't called the hooks, so leave them in place
    # for possible retry of import

    if module.__dict__.keys()==['__name__']:  # don't reload if already loaded!
        reload(module)

    try:
        for hook in getModuleHooks(module.__name__):
            hook(module)

    finally:
        # Ensure hooks are not called again, even if they fail
        postLoadHooks[module.__name__] = None


def getModuleHooks(moduleName):

    """Get list of hooks for 'moduleName'; error if module already loaded"""

    hooks = postLoadHooks.setdefault(moduleName,[])

    if hooks is None:
        raise AlreadyRead("Module already imported", moduleName)

    return hooks


def _setModuleHook(moduleName, hook):

    if moduleName in modules and postLoadHooks.get(moduleName) is None:
        # Module is already imported/loaded, just call the hook
        module = modules[moduleName]
        hook(module)
        return module

    getModuleHooks(moduleName).append(hook)
    return lazyModule(moduleName)



















def whenImported(moduleName, hook):

    """Call 'hook(module)' when module named 'moduleName' is first used

    'hook' must accept one argument: the module object named by 'moduleName',
    which must be a fully qualified (i.e. absolute) module name.  The hook
    should not raise any exceptions, or it may prevent later hooks from
    running.

    If the module has already been imported normally, 'hook(module)' is
    called immediately, and the module object is returned from this function.
    If the module has not been imported, or has only been imported lazily,
    then the hook is called when the module is first used, and a lazy import
    of the module is returned from this function.  If the module was imported
    lazily and used before calling this function, the hook is called
    immediately, and the loaded module is returned from this function.

    Note that using this function implies a possible lazy import of the
    specified module, and lazy importing means that any 'ImportError' will be
    deferred until the module is used.
    """

    if '.' in moduleName:
        # If parent is not yet imported, delay hook installation until the
        # parent is imported.
        splitpos = moduleName.rindex('.')
        whenImported(
            moduleName[:splitpos], lambda m: _setModuleHook(moduleName,hook)
        )
    else:
        return _setModuleHook(moduleName,hook)










def importObject(spec, globalDict=defaultGlobalDict):

    """Convert a possible string specifier to an object

    If 'spec' is a string or unicode object, import it using 'importString()',
    otherwise return it as-is.
    """

    if isinstance(spec,StringTypes):
        return importString(spec, globalDict)

    return spec


def importSequence(specs, globalDict=defaultGlobalDict):

    """Convert a string or list specifier to a list of objects.

    If 'specs' is a string or unicode object, treat it as a
    comma-separated list of import specifications, and return a
    list of the imported objects.

    If the result is not a string but is iterable, return a list
    with any string/unicode items replaced with their corresponding
    imports.
    """

    if isinstance(specs,StringTypes):
        return [importString(x.strip(),globalDict) for x in specs.split(',')]
    else:
        return [importObject(s,globalDict) for s in specs]










