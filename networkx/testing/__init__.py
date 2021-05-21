"""
Testing
=======

General guidelines for writing good tests:

- doctests always assume ``import networkx as nx`` so don't add that
- prefer pytest fixtures over classes with setup methods.
- use the ``@pytest.mark.parametrize``  decorator
- use ``pytest.importskip`` for numpy, scipy, pandas, and matplotlib b/c of PyPy.
  and add the module to the relevant entries in ``networkx/conftest.py``.

"""
from networkx.testing.utils import *
from networkx.testing.test import run
