#!/usr/bin/env python
from nose.tools import *
from networkx.utils import uniform_sequence,powerlaw_sequence,create_degree_sequence
import networkx.utils

def test_degree_sequences():
    seq=create_degree_sequence(10,uniform_sequence)
    assert_equal(len(seq), 10)
    seq=create_degree_sequence(10,powerlaw_sequence)
    assert_equal(len(seq), 10)
