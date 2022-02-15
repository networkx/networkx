import importlib
import importlib.util
import types
import os
import sys


__all__ = ["attach", "lazy_import"]


def attach(module_name, submodules=None, submod_attrs=None):
    """Attach lazily loaded submodules, and functions or other attributes.

    Typically, modules import submodules and attributes as follows::

      import mysubmodule
      import anothersubmodule

      from .foo import someattr

    The idea of  this function is to replace the `__init__.py`
    module's `__getattr__`, `__dir__`, and `__all__` attributes such that
    all imports work exactly the way they normally would, except that the
    actual import is delayed until the resulting module object is first used.

    The typical way to call this function, replacing the above imports, is::

      __getattr__, __lazy_dir__, __all__ = lazy.attach(
          __name__,
          ['mysubmodule', 'anothersubmodule'],
          {'foo': 'someattr'}
      )

    This functionality requires Python 3.7 or higher.

    Parameters
    ----------
    module_name : str
        Typically use __name__.
    submodules : set
        List of submodules to lazily import.
    submod_attrs : dict
        Dictionary of submodule -> list of attributes / functions.
        These attributes are imported as they are used.

    Returns
    -------
    __getattr__, __dir__, __all__

    """
    if submod_attrs is None:
        submod_attrs = {}

    if submodules is None:
        submodules = set()
    else:
        submodules = set(submodules)

    attr_to_modules = {
        attr: mod for mod, attrs in submod_attrs.items() for attr in attrs
    }

    __all__ = list(submodules | attr_to_modules.keys())

    def __getattr__(name):
        if name in submodules:
            return importlib.import_module(f"{module_name}.{name}")
        elif name in attr_to_modules:
            submod = importlib.import_module(f"{module_name}.{attr_to_modules[name]}")
            return getattr(submod, name)
        else:
            raise AttributeError(f"No {module_name} attribute {name}")

    def __dir__():
        return __all__

    if os.environ.get("EAGER_IMPORT", ""):
        for attr in set(attr_to_modules.keys()) | submodules:
            __getattr__(attr)

    return __getattr__, __dir__, list(__all__)


def lazy_import(fullname):
    """Return a lazily imported proxy for a module or library.

    We often see the following pattern::

      def myfunc():
          import scipy as sp
          sp.argmin(...)
          ....

    This is to prevent a library, in this case `scipy`, from being
    imported at function definition time, since that can be slow.

    This function provides a proxy module that, upon access, imports
    the actual module.  So the idiom equivalent to the above example is::

      sp = lazy.load("scipy")

      def myfunc():
          sp.argmin(...)
          ....

    The initial import time is fast because the actual import is delayed
    until the first attribute is requested. The overall import time may
    decrease as well for users that don't make use of large portions
    of the library.

    Parameters
    ----------
    fullname : str
        The full name of the package or subpackage to import.  For example::

          sp = lazy.load('scipy')  # import scipy as sp
          spla = lazy.load('scipy.linalg')  # import scipy.linalg as spla

    Returns
    -------
    pm : importlib.util._LazyModule
        Proxy module. Can be used like any regularly imported module.
        Actual loading of the module occurs upon first attribute request.

    """
    try:
        return sys.modules[fullname]
    except:
        pass

    # Not previously loaded -- look it up
    spec = importlib.util.find_spec(fullname)

    if spec is None:
        # module not found - construct a DelayedImportErrorModule
        spec = importlib.util.spec_from_loader(fullname, loader=None)
        module = importlib.util.module_from_spec(spec)
        tmp_loader = importlib.machinery.SourceFileLoader(module, path=None)
        loader = DelayedImportErrorLoader(tmp_loader)
        loader.exec_module(module)
        # dont add to sys.modules. The module wasn't found.
        return module

    module = importlib.util.module_from_spec(spec)
    sys.modules[fullname] = module

    loader = importlib.util.LazyLoader(spec.loader)
    loader.exec_module(module)

    return module


class DelayedImportErrorLoader(importlib.util.LazyLoader):
    def exec_module(self, module):
        super().exec_module(module)
        module.__class__ = DelayedImportErrorModule


class DelayedImportErrorModule(types.ModuleType):
    def __getattribute__(self, attr):
        """Trigger a ModuleNotFoundError upon attribute access"""
        spec = super().__getattribute__("__spec__")
        # allows isinstance and type functions to work without raising error
        if attr in ["__class__"]:
            return super().__getattribute__("__class__")

        raise ModuleNotFoundError(
            f"Delayed Report: module named '{spec.name}' not found.\n"
            "Reporting was Lazy -- delayed until module attributes accessed.\n"
            f"Most likely, {spec.name} is not installed"
        )
