import sys
import os
import importlib.util
import pytest

from networkx import lazy_import, lazy_package_import
from networkx.lazy_imports import DelayedImportErrorModule


def test_lazy_import_basics():
    math = lazy_import("math")
    anything_not_real = lazy_import("anything_not_real")

    # Now test that accessing attributes does what it should
    assert math.sin(math.pi) == pytest.approx(0, 1e-6)
    # poor-mans pytest.raises for testing errors on attribute access
    try:
        anything_not_real.pi
        assert False  # Should not get here
    except ModuleNotFoundError:
        pass
    assert isinstance(anything_not_real, DelayedImportErrorModule)
    # see if it changes for second access
    try:
        anything_not_real.pi
        assert False  # Should not get here
    except ModuleNotFoundError:
        pass


def test_lazy_impact_on_sys_modules():
    math = lazy_import("math")
    anything_not_real = lazy_import("anything_not_real")

    assert type(math) == importlib.types.ModuleType
    assert "math" in sys.modules
    assert type(anything_not_real) == DelayedImportErrorModule
    assert "anything_not_real" not in sys.modules

    # only do this if numpy is installed
    # np_test = pytest.importorskip("numpy")
    np = lazy_import("numpy")
    assert type(np) == importlib.types.ModuleType
    assert "numpy" in sys.modules

    np.pi  # trigger load of numpy

    assert type(np) == importlib.types.ModuleType
    assert "numpy" in sys.modules


def test_lazy_import_nonbuiltins():
    sp = lazy_import("scipy")
    np = lazy_import("numpy")
    if isinstance(sp, DelayedImportErrorModule):
        try:
            sp.pi
            assert False
        except ModuleNotFoundError:
            pass
    elif isinstance(np, DelayedImportErrorModule):
        try:
            np.sin(np.pi)
            assert False
        except ModuleNotFoundError:
            pass
    else:
        assert np.sin(sp.pi) == pytest.approx(0, 1e-6)


def test_lazy_package_import():
    name = "mymod"
    submods = ["mysubmodule", "anothersubmodule"]
    myall = {"not_real_submod": ["some_var_or_func"]}

    locls = {
        "lazy_package_import": lazy_package_import,
        "name": name,
        "submods": submods,
        "myall": myall,
    }
    s = "__getattr__, __lazy_dir__, __all__ = lazy_package_import(name, submods, myall)"

    exec(s, {}, locls)
    expected = {
        "lazy_package_import": lazy_package_import,
        "name": name,
        "submods": submods,
        "myall": myall,
        "__getattr__": None,
        "__lazy_dir__": None,
        "__all__": None,
    }
    assert locls.keys() == expected.keys()
    for k, v in locls.items():
        if k not in ("__getattr__", "__lazy_dir__", "__all__"):
            assert v == expected[k]
