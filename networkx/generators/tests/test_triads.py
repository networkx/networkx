# test_triads.py - unit tests for the triads module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.generators.triads` module."""
import pytest

from networkx import triad_graph


def test_triad_graph():
    G = triad_graph('030T')
    assert [tuple(e) for e in ('ab', 'ac', 'cb')] == sorted(G.edges())


def test_invalid_name():
    with pytest.raises(ValueError):
        triad_graph('bogus')
