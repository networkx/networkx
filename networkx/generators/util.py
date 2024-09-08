def assert_directedness_multi(G, *, directed=None, multigraph=None):
    """
    Assert that a graph has the desired directedness and multi-edge properties.
    """
    if directed is not None:
        if directed and not G.is_directed():
            raise ValueError("graph must be directed")
        if not directed and G.is_directed():
            raise ValueError("graph must not be directed")

    if multigraph is not None:
        if multigraph and not G.is_multigraph():
            raise ValueError("graph must be a multi-graph")
        if not multigraph and G.is_multigraph():
            raise ValueError("graph must not be a multi-graph")
