import networkx as nx
from itertools import combinations


__author__ = """Huston Hedinger (h@graphalchemist.com)"""
__all__ = ['dispersion_centrality']


def dispersion_centrality(G, u, v=None, exclude_nodes=None, normalized=True):
    """ A python implementation of 'dispersion' as defined by Lars Backstrom
    and Jon Kleinberg here: http://arxiv.org/pdf/1310.6753v1.pdf
    
    Parameters
    ----------
    G : graph
      A NetworkX graph
    u : node, required
      the ego node of the network
    v : node, optional
      Return only the dispersion value for node v
    exclude_nodes : list of nodes, optional
      Exclude nodes from score
    normalized : bool, optional
      If True (default) normalize by the embededness of the nodes (u and v).
    """

    G_u = G
    dispersion = dict.fromkeys(G_u, 0)
    u_nbrs = set(G[u])

    for v in u_nbrs:
        ST = set(n for n in G[v] if n in u_nbrs)
        set_uv=set([u,v])
        possib = combinations(ST, 2)
        total = 0
        for p in possib:
            s = p[0]
            t = p[1]
            nbrs_s = u_nbrs.intersection(G[s]) - set_uv
            if nbrs_s.isdisjoint(G[t]):
                total += 1
        embededness = len(ST)
    
        if normalized == True:
            if embededness != 0:
                norm_disp = (total/embededness)
            elif embededness == 0:
                norm_disp = total
            dispersion[v] = {'norm_disp' : norm_disp}
        else:
            dispersion[v] = {'abs_disp': total}
    return dispersion
