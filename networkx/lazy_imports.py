import importlib.util
import types
import os
import sys
import pytest


__all__ = ["lazy_import", "lazy_package_import", "lazy_importorskip"]


def lazy_package_import(module_name, submodules=None, submod_attrs=None):
    """Install lazily loaded submodules, and functions or other attributes.

    Typically, modules import submodules and attributes as follows::

      import mysubmodule
      import anothersubmodule
      from .foo import someattr

    The idea of the lazy package import is to replace the `__init__.py`
    module's `__getattr__`, `__dir__`, and `__all__` attributes such that
    all imports work exactly the way they normally would, except that the
    actual import is delayed until the resulting module object is first used.

    The typical way to call this function, replacing the above imports, is::

      __getattr__, __lazy_dir__, __all__ = install_lazy(
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
        These attributes are created the first time the submodule
        is used.

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


class DelayedImportErrorLoader(importlib.util.LazyLoader):
    def exec_module(self, module):
        """Make the module load lazily."""
        module.__spec__.loader = self.loader
        module.__loader__ = self.loader
        # Don't need to worry about deep-copying as trying to set an attribute
        # on an object would have triggered the load,
        # e.g. ``module.__spec__.loader = None`` would trigger a load from
        # trying to access module.__spec__.
        loader_state = {}
        loader_state["__dict__"] = module.__dict__.copy()
        loader_state["__class__"] = module.__class__
        module.__spec__.loader_state = loader_state
        module.__class__ = DelayedImportErrorModule


class DelayedImportErrorModule(types.ModuleType):
    """A subclass of ModuleType which trigger an ImportError upon attribute access

    Based on importlib.util._LazyModule
    """

    def __getattribute__(self, attr):
        spec = super().__getattribute__("__spec__")
        raise ModuleNotFoundError(
            f"Delayed Report: module named '{spec.name}' not found.\n"
            "Reporting was Lazy -- delayed until module attributes accessed.\n"
            f"Most likely, {spec.name} is not installed"
        )


def lazy_importorskip(modname, minversion=None, reason=None):
    module = pytest.importorskip(modname, minversion, reason)
    if isinstance(module, DelayedImportErrorModule):
        if reason is None:
            reason = "Could not import {modname!r}. Lazy import delayed reporting."
        raise pytest.skip(reason, allow_module_level=True)
    return module


def lazy_import(fullname):
    """Return a lazily imported proxy for a module or library.

    We often see the following pattern::

      def myfunc():
          import scipy
          ....

    This is to prevent a library, in this case `scipy`, from being
    imported at function definition time, since that can be slow.
    This function provides a proxy module that, upon access, imports
    the actual module.

    Parameters
    ----------

    fullname : str
        The full name of the package or subpackage to import.  For example::
          sp = lazy_import('scipy')  # import scipy as sp
          spla = lazy_import('scipy.linalg')  # import scipy.linalg as spla

    Returns
    -------

    pm : importlib.util._LazyModule
        Proxy module. Can be used like any regularly imported module.
    """
    try:
        return sys.modules[fullname]
    except:
        pass

    # Not previously loaded -- look it up
    spec = importlib.util.find_spec(fullname)

    if spec is not None:
        module = importlib.util.module_from_spec(spec)

        # Make module with proper locking and get it inserted into sys.modules.
        loader = importlib.util.LazyLoader(spec.loader)
        sys.modules[fullname] = module
        loader.exec_module(module)
        return module

    # package not found - construct delayed error module
    spec = importlib.util.spec_from_loader(fullname, loader=None)
    module = importlib.util.module_from_spec(spec)
    tmp_loader = importlib.machinery.SourceFileLoader(module, path=None)
    loader = DelayedImportErrorLoader(tmp_loader)

    sys.modules[fullname] = module
    loader.exec_module(module)
    return module
