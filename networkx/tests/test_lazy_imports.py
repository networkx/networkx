import sys
import os
import importlib.util
import pytest

from networkx import lazy_import, lazy_package_import


def test_lazy_import():
    np = lazy_import("numpy")
    anything_not_real = lazy_import("anything_not_real")

    # Now test that accessing attributes does what it should
    assert np.sin(np.pi) == pytest.approx(0, 1e-6)
    # poor-mans pytest.raises for testing errors on attribute access
    try:
        anything_not_real.pi
        assert False  # Should not get here
    except ModuleNotFoundError:
        pass


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
