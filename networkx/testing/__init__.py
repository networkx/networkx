"""
Testing
=======

General guidelines for writing good tests:

- doctests always assume ``import networkx as nx`` so don't add that
- Prefer pytest fixtures over classes with setup methods.
- use the following decorators (``@pytest.mark.parametrize``, ``@pytest.mark.skipif``, ``@pytest.mark.xfail``, ``@pytest.mark.slow``)
- use ``pytest.importskip`` for numpy, scipy, pandas, and matplotlib b/c of PyPy.
- something about ``networkx/conftest.py``
"""
from networkx.testing.utils import *
from networkx.testing.test import run
