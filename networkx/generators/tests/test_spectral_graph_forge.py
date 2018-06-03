from nose import SkipTest
from nose.tools import assert_true, assert_raises, assert_false

from networkx import is_isomorphic
from networkx.exception import NetworkXError
from networkx.testing import assert_nodes_equal
from networkx.generators.spectral_graph_forge import spectral_graph_forge
from networkx.generators import karate_club_graph


def test_spectral_graph_forge():
    numpy = 1  # nosetests attribute, use nosetests -a 'not numpy' to skip test
    scipy = 1

    try:
        import numpy
    except ImportError:
        raise SkipTest('NumPy not available.')
    try:
        import scipy
    except ImportError:
        raise SkipTest("SciPy not available")

    G = karate_club_graph()

    seed = 54321

    # common cases, just checking node number preserving and difference
    # between identity and modularity cases
    H = spectral_graph_forge(G, 0.1, transformation='identity', seed=seed)
    assert_nodes_equal(G, H)

    I = spectral_graph_forge(G, 0.1, transformation='identity', seed=seed)
    assert_nodes_equal(G, H)
    assert_true(is_isomorphic(I, H))

    I = spectral_graph_forge(G, 0.1, transformation='modularity', seed=seed)
    assert_nodes_equal(G, I)

    assert_false(is_isomorphic(I, H))

    # with all the eigenvectors, output graph is identical to the input one
    H = spectral_graph_forge(G, 1, transformation='modularity', seed=seed)
    assert_nodes_equal(G, H)
    assert_true(is_isomorphic(G, H))

    # invalid alpha input value, it is silently truncated in [0,1]
    H = spectral_graph_forge(G, -1, transformation='identity', seed=seed)
    assert_nodes_equal(G, H)

    H = spectral_graph_forge(G, 10, transformation='identity', seed=seed)
    assert_nodes_equal(G, H)
    assert_true(is_isomorphic(G, H))

    # invalid transformation mode, checking the error raising
    assert_raises(NetworkXError,
                  spectral_graph_forge, G, 0.1, transformation='unknown',
                  seed=seed)
