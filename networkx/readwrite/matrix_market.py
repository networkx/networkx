"""
Read graphs in the MatrixMarket format.

MatixMarket is a graph storage created by NIST.

Format
------
See https://math.nist.gov/MatrixMarket/formats.html

"""
__author__ = "Henry Carscadden"
__email__ = "hlc5v@virginia.edu"

__all__ = ["read_mtx", "write_mtx"]

import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import open_file
import scipy.io


@open_file(0, mode="rb")
def read_mtx(path, parallel_edges=False, create_using=None):
    """Read graph in MatrixMarket format from path.

    Parameters
    ----------
    path : file or string
       File or filename to write.
       Filenames ending in .gz will be decompressed.

    parallel_edges: Boolean
        If this is True, create_using is a multigraph, and A is an integer matrix, then entry (i, j) in the
        matrix is interpreted as the number of parallel edges joining vertices i and j in the graph. If it is False,
        then the entries in the matrix are interpreted as the weight of a single edge joining the vertices.

    create_using: NetworkX Graph type (default: nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.



    Returns
    -------
    graph: NetworkX graph
        If create_using is not specified, a nx.Graph is returned.

    Notes
    -----
    Any weights stored in the MartixMarket file will saved in the edge attribute "weight".


    """

    mtx = scipy.io.mmread(path)
    # From https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.mmread.html?highlight=mmread#scipy.io.mmread,
    # the matrix will be one of two types.
    if isinstance(mtx, scipy.sparse.coo_matrix):
        return nx.from_scipy_sparse_matrix(
            mtx, create_using=create_using, parallel_edges=parallel_edges
        )
    elif isinstance(mtx, np.ndarray):
        return nx.from_numpy_array(
            mtx, create_using=create_using, parallel_edges=parallel_edges
        )
    else:
        raise TypeError("Matrix is of an unexpected type.")


@open_file(0, mode="wb")
def write_mtx(G, path):
    """Read graph in MatrixMarket format from path.

    Parameters
    ----------
    G: A NetworkX Graph
        This is the graph that will be output to a MatrixMarket file.
    path : file or string
       File or filename to write.
       Filenames ending in .gz will be decompressed.





    Returns
    -------
    None.

    Notes
    -----
    Any weights stored in the MartixMarket file will saved in the edge attribute "weight".


    """

    mtx = nx.to_scipy_sparse_matrix(G)
    scipy.io.mmwrite(path, mtx)
