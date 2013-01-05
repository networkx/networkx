from nose.tools import *
from nose import SkipTest
import networkx as nx
from networkx.utils import *

def test_is_string_like():
    assert_true(is_string_like("aaaa"))
    assert_false(is_string_like(None))
    assert_false(is_string_like(123))

def test_iterable():
    assert_false(iterable(None))
    assert_false(iterable(10))
    assert_true(iterable([1,2,3]))
    assert_true(iterable((1,2,3)))
    assert_true(iterable({1:"A",2:"X"}))
    assert_true(iterable("ABC"))

def test_graph_iterable():
    K=nx.complete_graph(10)
    assert_true(iterable(K))
    assert_true(iterable(K.nodes_iter()))
    assert_true(iterable(K.edges_iter()))

def test_is_list_of_ints():
    assert_true(is_list_of_ints([1,2,3,42]))
    assert_false(is_list_of_ints([1,2,3,"kermit"]))

def test_random_number_distribution():
    # smoke test only
    z=uniform_sequence(20)
    z=powerlaw_sequence(20,exponent=2.5)
    z=pareto_sequence(20,exponent=1.5)
    z=discrete_sequence(20,distribution=[0,0,0,0,1,1,1,1,2,2,3])

class TestNumpyArray(object):
    numpy=1 # nosetests attribute, use nosetests -a 'not numpy' to skip test
    @classmethod
    def setupClass(cls):
        global numpy
        global assert_equal
        global assert_almost_equal
        try:
            import numpy
            from numpy.testing import assert_equal,assert_almost_equal
        except ImportError:
             raise SkipTest('NumPy not available.')

    def test_dict_to_numpy_array1(self):
        d = {'a':1,'b':2}
        a = dict_to_numpy_array1(d)
        assert_equal(a, numpy.array([1,2]))
        a = dict_to_numpy_array1(d, mapping = {'b':0,'a':1})
        assert_equal(a, numpy.array([2,1]))

    def test_dict_to_numpy_array2(self):
        d = {'a': {'a':1,'b':2},
             'b': {'a':10,'b':20}}
        a = dict_to_numpy_array(d)
        assert_equal(a, numpy.array([[1,2],[10,20]]))
        a = dict_to_numpy_array2(d, mapping = {'b':0,'a':1})
        assert_equal(a, numpy.array([[20,10],[2,1]]))


    def test_dict_to_numpy_array(self):
        d = {'a': {'a':1,'b':2},
             'b': {'a':10,'b':20}}
        a = dict_to_numpy_array(d)
        assert_equal(a, numpy.array([[1,2],[10,20]]))
        d = {'a':1,'b':2}
        a = dict_to_numpy_array1(d)
        assert_equal(a, numpy.array([1,2]))
