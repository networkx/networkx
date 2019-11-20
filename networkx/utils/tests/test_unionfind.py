import networkx as nx


def test_unionfind():
    # Fixed by: 2cddd5958689bdecdcd89b91ac9aaf6ce0e4f6b8
    # Previously (in 2.x), the UnionFind class could handle mixed types.
    # But in Python 3.x, this causes a TypeError such as:
    #   TypeError: unorderable types: str() > int()
    #
    # Now we just make sure that no exception is raised.
    x = nx.utils.UnionFind()
    x.union(0, 'a')


def test_subtree_union():
    # See https://github.com/networkx/networkx/pull/3224
    # (35db1b551ee65780794a357794f521d8768d5049).
    # Test if subtree unions hare handled correctly by to_sets().
    uf = nx.utils.UnionFind()
    uf.union(1, 2)
    uf.union(3, 4)
    uf.union(4, 5)
    uf.union(1, 5)
    assert list(uf.to_sets()) == [set([1, 2, 3, 4, 5])]
