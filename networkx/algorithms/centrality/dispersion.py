from itertools import combinations

__author__ = "\n".join(['Ben Edwards (bedwards@cs.unm.edu)',
                        'Huston Hedinger (h@graphalchemist.com)',
                        'Dan Schult (dschult@colgate.edu)'])

__all__ = ['dispersion']


def dispersion(G, u=None, v=None, normalized=True, alpha=1.0, b=0.0, c=0.0):
    r"""  A python implementation of 'dispersion' as defined by Lars Backstrom
    and Jon Kleinberg [1]_.
    
    A link between two actors ('u' and 'v') has a high dispersion when their mutual 
    ties ('s' and 't') are not well connected with each other.
    
    .. math::

    Parameters
    ----------
    G : graph
      A NetworkX graph
    u : node, optional
      the source node for the dispersion score (e.g. ego node of the network)
    v : node, optional
      the target node for the dispersion score if specified
    
    Note:  Typical usage would be to run dispersion on ego network (G_u) were u is specified.
    Running disperion on larger networks without 'u' or 'v' specified can be computationally expensive.

    normalized : bool
      If True (default) normalize by the embededness of the nodes (u and v).
    
    Returns
    -------
    nodes : dictionary
       If u or v is specified, returns a dictionary of nodes with dispersion score 
       for all "target" nodes
       If neither u or v is specified, returns a dictionary of dictionaries for all nodes 
       'u' in the graph with a dispersion score for each node 'v'.

    References
    ----------
    .. [1] Romantic Partnerships and the Dispersion of Social Ties:
        A Network Analysis of Relationship Status on Facebook.
        Lars Backstrom, Jon Kleinberg.
        http://arxiv.org/pdf/1310.6753v1.pdf
    
    """

    def _dispersion(G_u, u, v):
        """dispersion for all nodes 'v' in a ego network G_u of node 'u'"""
        u_nbrs = set(G_u[u])
        ST = set(n for n in G_u[v] if n in u_nbrs)
        set_uv=set([u,v])
        #all possible ties of connections that u and b share
        possib = combinations(ST, 2)
        total = 0
        for (s,t) in possib:
            #neighbors of s that are in G_u, not including u and v
            nbrs_s = u_nbrs.intersection(G_u[s]) - set_uv
            #s and t are not directly connected
            if not t in nbrs_s:
                #s and t do not share a connection
                if nbrs_s.isdisjoint(G_u[t]):
                    #tick for disp(u, v)
                    total += 1
        #neighbors that u and v share
        embededness = len(ST)

        if normalized:
            if embededness + c != 0:
                norm_disp = ((total + b)**alpha)/(embededness + c)
            else:
                norm_disp = (total+b)**alpha
            dispersion = norm_disp

        else:
            dispersion = total

        return dispersion

    if u is None:
        # v and u are not specified
        if v is None:
            results = dict((n,{}) for n in G)
            for u in G:
                for v in G[u]:
                    results[u][v] = _dispersion(G, u, v)
        # u is not specified, but v is
        else:
            results = dict.fromkeys(G[v], {})
            for u in G[v]:
                results[u] = _dispersion(G, v, u)
    else:
        # u is specified with no target v
        if v is None:
            results = dict.fromkeys(G[u], {})
            for v in G[u]:
                results[v] = _dispersion(G, u, v)
        # both u and v are specified
        else:
            results = _dispersion(G, u, v)

    return results
