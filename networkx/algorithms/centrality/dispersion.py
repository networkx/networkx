from itertools import combinations

__author__ = "\n".join(['Ben Edwards (bedwards@cs.unm.edu)',
                        'Huston Hedinger (h@graphalchemist.com)',
                        'Dan Schult (dschult@colgate.edu)'])

__all__ = ['dispersion']


def dispersion(G, u=None, v=None, normalized=True, alpha=1.0, b=0.0, c=0.0):
    r""" A python implementation of 'dispersion' as defined by Lars Backstrom
    and Jon Kleinberg [1]_.
    
    Where a link between two actors ('u' and 'v') has a high dispersion when their mutual 
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
    
    Note: when not specifying 'u' or 'v' on larger networks can take some time.
    Typical usage would be to run dispersion on ego network (G_u) with u specified 

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
        """ dispersion for all nodes 'v' in a ego network G_u of node 'u' """
        u_nbrs = set(G_u[u])
        ST = set(n for n in G_u[v] if n in u_nbrs)
        set_uv=set([u,v])
        possib = combinations(ST, 2)
        total = 0
        for (s,t) in possib:
            nbrs_s = u_nbrs.intersection(G_u[s]) - set_uv
            if nbrs_s.isdisjoint(G_u[t]):
                total += 1
        embededness = len(ST)

        if normalized == True:
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
            results = dict.fromkeys(G, {})
            for u in G:
                for v in G[u]:
                    results[u][v] = _dispersion(G, u, v)
        # u is not specified, but v is
        else:
            results = dict.fromkeys(G, {})
            for u in G:
                results[u] = _dispersion(G, u, v)
    else:
        # u is specified with no target v
        if v is None:
            results = dict.fromkeys(G, {})
            for v in G:
                results[v] = _dispersion(G, u, v)
        # both u and v are specified
        else:
            results = {v : _dispersion(G, u, v)}

    return results
