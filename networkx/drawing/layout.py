"""
******
Layout
******

Node positioning algorithms for graph drawing.

For `random_layout()` the possible resulting shape
is a square of side [0, scale] (default: [0, 1])
Changing `center` shifts the layout by that amount.

For the other layout routines, the extent is
[center - scale, center + scale] (default: [-1, 1]).

Warning: Most layout routines have only been tested in 2-dimensions.

"""
import networkx as nx
from networkx.utils import np_random_state

__all__ = [
    "bipartite_layout",
    "circular_layout",
    "kamada_kawai_layout",
    "random_layout",
    "rescale_layout",
    "rescale_layout_dict",
    "shell_layout",
    "spring_layout",
    "spectral_layout",
    "planar_layout",
    "fruchterman_reingold_layout",
    "spiral_layout",
    "multipartite_layout",
]


def _process_params(G, center, dim):
    # Some boilerplate code.
    import numpy as np

    if not isinstance(G, nx.Graph):
        empty_graph = nx.Graph()
        empty_graph.add_nodes_from(G)
        G = empty_graph

    if center is None:
        center = np.zeros(dim)
    else:
        center = np.asarray(center)

    if len(center) != dim:
        msg = "length of center coordinates must match dimension of layout"
        raise ValueError(msg)

    return G, center


@np_random_state(3)
def random_layout(G, center=None, dim=2, seed=None):
    """Position nodes uniformly at random in the unit square.

    For every node, a position is generated by choosing each of dim
    coordinates uniformly at random on the interval [0.0, 1.0).

    NumPy (http://scipy.org) is required for this function.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.

    center : array-like or None
        Coordinate pair around which to center the layout.

    dim : int
        Dimension of layout.

    seed : int, RandomState instance or None  optional (default=None)
        Set the random state for deterministic node layouts.
        If int, `seed` is the seed used by the random number generator,
        if numpy.random.RandomState instance, `seed` is the random
        number generator,
        if None, the random number generator is the RandomState instance used
        by numpy.random.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node

    Examples
    --------
    >>> G = nx.lollipop_graph(4, 3)
    >>> pos = nx.random_layout(G)

    """
    import numpy as np

    G, center = _process_params(G, center, dim)
    pos = seed.rand(len(G), dim) + center
    pos = pos.astype(np.float32)
    pos = dict(zip(G, pos))

    return pos


def circular_layout(G, scale=1, center=None, dim=2):
    # dim=2 only
    """Position nodes on a circle.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.

    scale : number (default: 1)
        Scale factor for positions.

    center : array-like or None
        Coordinate pair around which to center the layout.

    dim : int
        Dimension of layout.
        If dim>2, the remaining dimensions are set to zero
        in the returned positions.
        If dim<2, a ValueError is raised.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node

    Raises
    ------
    ValueError
        If dim < 2

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> pos = nx.circular_layout(G)

    Notes
    -----
    This algorithm currently only works in two dimensions and does not
    try to minimize edge crossings.

    """
    import numpy as np

    if dim < 2:
        raise ValueError("cannot handle dimensions < 2")

    G, center = _process_params(G, center, dim)

    paddims = max(0, (dim - 2))

    if len(G) == 0:
        pos = {}
    elif len(G) == 1:
        pos = {nx.utils.arbitrary_element(G): center}
    else:
        # Discard the extra angle since it matches 0 radians.
        theta = np.linspace(0, 1, len(G) + 1)[:-1] * 2 * np.pi
        theta = theta.astype(np.float32)
        pos = np.column_stack(
            [np.cos(theta), np.sin(theta), np.zeros((len(G), paddims))]
        )
        pos = rescale_layout(pos, scale=scale) + center
        pos = dict(zip(G, pos))

    return pos


def shell_layout(G, nlist=None, rotate=None, scale=1, center=None, dim=2):
    """Position nodes in concentric circles.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.

    nlist : list of lists
       List of node lists for each shell.

    rotate : angle in radians (default=pi/len(nlist))
       Angle by which to rotate the starting position of each shell
       relative to the starting position of the previous shell.
       To recreate behavior before v2.5 use rotate=0.

    scale : number (default: 1)
        Scale factor for positions.

    center : array-like or None
        Coordinate pair around which to center the layout.

    dim : int
        Dimension of layout, currently only dim=2 is supported.
        Other dimension values result in a ValueError.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node

    Raises
    ------
    ValueError
        If dim != 2

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> shells = [[0], [1, 2, 3]]
    >>> pos = nx.shell_layout(G, shells)

    Notes
    -----
    This algorithm currently only works in two dimensions and does not
    try to minimize edge crossings.

    """
    import numpy as np

    if dim != 2:
        raise ValueError("can only handle 2 dimensions")

    G, center = _process_params(G, center, dim)

    if len(G) == 0:
        return {}
    if len(G) == 1:
        return {nx.utils.arbitrary_element(G): center}

    if nlist is None:
        # draw the whole graph in one shell
        nlist = [list(G)]

    radius_bump = scale / len(nlist)

    if len(nlist[0]) == 1:
        # single node at center
        radius = 0.0
    else:
        # else start at r=1
        radius = radius_bump

    if rotate is None:
        rotate = np.pi / len(nlist)
    first_theta = rotate
    npos = {}
    for nodes in nlist:
        # Discard the last angle (endpoint=False) since 2*pi matches 0 radians
        theta = (
            np.linspace(0, 2 * np.pi, len(nodes), endpoint=False, dtype=np.float32)
            + first_theta
        )
        pos = radius * np.column_stack([np.cos(theta), np.sin(theta)]) + center
        npos.update(zip(nodes, pos))
        radius += radius_bump
        first_theta += rotate

    return npos


def bipartite_layout(
    G, nodes, align="vertical", scale=1, center=None, aspect_ratio=4 / 3
):
    """Position nodes in two straight lines.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.

    nodes : list or container
        Nodes in one node set of the bipartite graph.
        This set will be placed on left or top.

    align : string (default='vertical')
        The alignment of nodes. Vertical or horizontal.

    scale : number (default: 1)
        Scale factor for positions.

    center : array-like or None
        Coordinate pair around which to center the layout.

    aspect_ratio : number (default=4/3):
        The ratio of the width to the height of the layout.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node.

    Examples
    --------
    >>> G = nx.bipartite.gnmk_random_graph(3, 5, 10, seed=123)
    >>> top = nx.bipartite.sets(G)[0]
    >>> pos = nx.bipartite_layout(G, top)

    Notes
    -----
    This algorithm currently only works in two dimensions and does not
    try to minimize edge crossings.

    """

    import numpy as np

    if align not in ("vertical", "horizontal"):
        msg = "align must be either vertical or horizontal."
        raise ValueError(msg)

    G, center = _process_params(G, center=center, dim=2)
    if len(G) == 0:
        return {}

    height = 1
    width = aspect_ratio * height
    offset = (width / 2, height / 2)

    top = set(nodes)
    bottom = set(G) - top
    nodes = list(top) + list(bottom)

    left_xs = np.repeat(0, len(top))
    right_xs = np.repeat(width, len(bottom))
    left_ys = np.linspace(0, height, len(top))
    right_ys = np.linspace(0, height, len(bottom))

    top_pos = np.column_stack([left_xs, left_ys]) - offset
    bottom_pos = np.column_stack([right_xs, right_ys]) - offset

    pos = np.concatenate([top_pos, bottom_pos])
    pos = rescale_layout(pos, scale=scale) + center
    if align == "horizontal":
        pos = np.flip(pos, 1)
    pos = dict(zip(nodes, pos))
    return pos


@np_random_state(10)
def spring_layout(
    G,
    k=None,
    pos=None,
    fixed=None,
    iterations=50,
    threshold=1e-4,
    weight="weight",
    scale=1,
    center=None,
    dim=2,
    seed=None,
):
    """Position nodes using Fruchterman-Reingold force-directed algorithm.

    The algorithm simulates a force-directed representation of the network
    treating edges as springs holding nodes close, while treating nodes
    as repelling objects, sometimes called an anti-gravity force.
    Simulation continues until the positions are close to an equilibrium.

    There are some hard-coded values: minimal distance between
    nodes (0.01) and "temperature" of 0.1 to ensure nodes don't fly away.
    During the simulation, `k` helps determine the distance between nodes,
    though `scale` and `center` determine the size and place after
    rescaling occurs at the end of the simulation.

    Fixing some nodes doesn't allow them to move in the simulation.
    It also turns off the rescaling feature at the simulation's end.
    In addition, setting `scale` to `None` turns off rescaling.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.

    k : float (default=None)
        Optimal distance between nodes.  If None the distance is set to
        1/sqrt(n) where n is the number of nodes.  Increase this value
        to move nodes farther apart.

    pos : dict or None  optional (default=None)
        Initial positions for nodes as a dictionary with node as keys
        and values as a coordinate list or tuple.  If None, then use
        random initial positions.

    fixed : list or None  optional (default=None)
        Nodes to keep fixed at initial position.
        Nodes not in ``G.nodes`` are ignored.
        ValueError raised if `fixed` specified and `pos` not.

    iterations : int  optional (default=50)
        Maximum number of iterations taken

    threshold: float optional (default = 1e-4)
        Threshold for relative error in node position changes.
        The iteration stops if the error is below this threshold.

    weight : string or None   optional (default='weight')
        The edge attribute that holds the numerical value used for
        the edge weight.  Larger means a stronger attractive force.
        If None, then all edge weights are 1.

    scale : number or None (default: 1)
        Scale factor for positions. Not used unless `fixed is None`.
        If scale is None, no rescaling is performed.

    center : array-like or None
        Coordinate pair around which to center the layout.
        Not used unless `fixed is None`.

    dim : int
        Dimension of layout.

    seed : int, RandomState instance or None  optional (default=None)
        Set the random state for deterministic node layouts.
        If int, `seed` is the seed used by the random number generator,
        if numpy.random.RandomState instance, `seed` is the random
        number generator,
        if None, the random number generator is the RandomState instance used
        by numpy.random.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> pos = nx.spring_layout(G)

    # The same using longer but equivalent function name
    >>> pos = nx.fruchterman_reingold_layout(G)
    """
    import numpy as np

    G, center = _process_params(G, center, dim)

    if fixed is not None:
        if pos is None:
            raise ValueError("nodes are fixed without positions given")
        for node in fixed:
            if node not in pos:
                raise ValueError("nodes are fixed without positions given")
        nfixed = {node: i for i, node in enumerate(G)}
        fixed = np.asarray([nfixed[node] for node in fixed if node in nfixed])

    if pos is not None:
        # Determine size of existing domain to adjust initial positions
        dom_size = max(coord for pos_tup in pos.values() for coord in pos_tup)
        if dom_size == 0:
            dom_size = 1
        pos_arr = seed.rand(len(G), dim) * dom_size + center

        for i, n in enumerate(G):
            if n in pos:
                pos_arr[i] = np.asarray(pos[n])
    else:
        pos_arr = None
        dom_size = 1

    if len(G) == 0:
        return {}
    if len(G) == 1:
        return {nx.utils.arbitrary_element(G.nodes()): center}

    try:
        # Sparse matrix
        if len(G) < 500:  # sparse solver for large graphs
            raise ValueError
        A = nx.to_scipy_sparse_array(G, weight=weight, dtype="f")
        if k is None and fixed is not None:
            # We must adjust k by domain size for layouts not near 1x1
            nnodes, _ = A.shape
            k = dom_size / np.sqrt(nnodes)
        pos = _sparse_fruchterman_reingold(
            A, k, pos_arr, fixed, iterations, threshold, dim, seed
        )
    except ValueError:
        A = nx.to_numpy_array(G, weight=weight)
        if k is None and fixed is not None:
            # We must adjust k by domain size for layouts not near 1x1
            nnodes, _ = A.shape
            k = dom_size / np.sqrt(nnodes)
        pos = _fruchterman_reingold(
            A, k, pos_arr, fixed, iterations, threshold, dim, seed
        )
    if fixed is None and scale is not None:
        pos = rescale_layout(pos, scale=scale) + center
    pos = dict(zip(G, pos))
    return pos


fruchterman_reingold_layout = spring_layout


@np_random_state(7)
def _fruchterman_reingold(
    A, k=None, pos=None, fixed=None, iterations=50, threshold=1e-4, dim=2, seed=None
):
    # Position nodes in adjacency matrix A using Fruchterman-Reingold
    # Entry point for NetworkX graph is fruchterman_reingold_layout()
    import numpy as np

    try:
        nnodes, _ = A.shape
    except AttributeError as err:
        msg = "fruchterman_reingold() takes an adjacency matrix as input"
        raise nx.NetworkXError(msg) from err

    if pos is None:
        # random initial positions
        pos = np.asarray(seed.rand(nnodes, dim), dtype=A.dtype)
    else:
        # make sure positions are of same type as matrix
        pos = pos.astype(A.dtype)

    # optimal distance between nodes
    if k is None:
        k = np.sqrt(1.0 / nnodes)
    # the initial "temperature"  is about .1 of domain area (=1x1)
    # this is the largest step allowed in the dynamics.
    # We need to calculate this in case our fixed positions force our domain
    # to be much bigger than 1x1
    t = max(max(pos.T[0]) - min(pos.T[0]), max(pos.T[1]) - min(pos.T[1])) * 0.1
    # simple cooling scheme.
    # linearly step down by dt on each iteration so last iteration is size dt.
    dt = t / float(iterations + 1)
    delta = np.zeros((pos.shape[0], pos.shape[0], pos.shape[1]), dtype=A.dtype)
    # the inscrutable (but fast) version
    # this is still O(V^2)
    # could use multilevel methods to speed this up significantly
    for iteration in range(iterations):
        # matrix of difference between points
        delta = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
        # distance between points
        distance = np.linalg.norm(delta, axis=-1)
        # enforce minimum distance of 0.01
        np.clip(distance, 0.01, None, out=distance)
        # displacement "force"
        displacement = np.einsum(
            "ijk,ij->ik", delta, (k * k / distance ** 2 - A * distance / k)
        )
        # update positions
        length = np.linalg.norm(displacement, axis=-1)
        length = np.where(length < 0.01, 0.1, length)
        delta_pos = np.einsum("ij,i->ij", displacement, t / length)
        if fixed is not None:
            # don't change positions of fixed nodes
            delta_pos[fixed] = 0.0
        pos += delta_pos
        # cool temperature
        t -= dt
        if (np.linalg.norm(delta_pos) / nnodes) < threshold:
            break
    return pos


@np_random_state(7)
def _sparse_fruchterman_reingold(
    A, k=None, pos=None, fixed=None, iterations=50, threshold=1e-4, dim=2, seed=None
):
    # Position nodes in adjacency matrix A using Fruchterman-Reingold
    # Entry point for NetworkX graph is fruchterman_reingold_layout()
    # Sparse version
    import numpy as np
    import scipy as sp
    import scipy.sparse  # call as sp.sparse

    try:
        nnodes, _ = A.shape
    except AttributeError as err:
        msg = "fruchterman_reingold() takes an adjacency matrix as input"
        raise nx.NetworkXError(msg) from err
    # make sure we have a LIst of Lists representation
    try:
        A = A.tolil()
    except AttributeError:
        A = (sp.sparse.coo_array(A)).tolil()

    if pos is None:
        # random initial positions
        pos = np.asarray(seed.rand(nnodes, dim), dtype=A.dtype)
    else:
        # make sure positions are of same type as matrix
        pos = pos.astype(A.dtype)

    # no fixed nodes
    if fixed is None:
        fixed = []

    # optimal distance between nodes
    if k is None:
        k = np.sqrt(1.0 / nnodes)
    # the initial "temperature"  is about .1 of domain area (=1x1)
    # this is the largest step allowed in the dynamics.
    t = max(max(pos.T[0]) - min(pos.T[0]), max(pos.T[1]) - min(pos.T[1])) * 0.1
    # simple cooling scheme.
    # linearly step down by dt on each iteration so last iteration is size dt.
    dt = t / float(iterations + 1)

    displacement = np.zeros((dim, nnodes))
    for iteration in range(iterations):
        displacement *= 0
        # loop over rows
        for i in range(A.shape[0]):
            if i in fixed:
                continue
            # difference between this row's node position and all others
            delta = (pos[i] - pos).T
            # distance between points
            distance = np.sqrt((delta ** 2).sum(axis=0))
            # enforce minimum distance of 0.01
            distance = np.where(distance < 0.01, 0.01, distance)
            # the adjacency matrix row
            Ai = A.getrowview(i).toarray()  # TODO: revisit w/ sparse 1D container
            # displacement "force"
            displacement[:, i] += (
                delta * (k * k / distance ** 2 - Ai * distance / k)
            ).sum(axis=1)
        # update positions
        length = np.sqrt((displacement ** 2).sum(axis=0))
        length = np.where(length < 0.01, 0.1, length)
        delta_pos = (displacement * t / length).T
        pos += delta_pos
        # cool temperature
        t -= dt
        if (np.linalg.norm(delta_pos) / nnodes) < threshold:
            break
    return pos


def kamada_kawai_layout(
    G, dist=None, pos=None, weight="weight", scale=1, center=None, dim=2
):
    """Position nodes using Kamada-Kawai path-length cost-function.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.

    dist : dict (default=None)
        A two-level dictionary of optimal distances between nodes,
        indexed by source and destination node.
        If None, the distance is computed using shortest_path_length().

    pos : dict or None  optional (default=None)
        Initial positions for nodes as a dictionary with node as keys
        and values as a coordinate list or tuple.  If None, then use
        circular_layout() for dim >= 2 and a linear layout for dim == 1.

    weight : string or None   optional (default='weight')
        The edge attribute that holds the numerical value used for
        the edge weight.  If None, then all edge weights are 1.

    scale : number (default: 1)
        Scale factor for positions.

    center : array-like or None
        Coordinate pair around which to center the layout.

    dim : int
        Dimension of layout.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> pos = nx.kamada_kawai_layout(G)
    """
    import numpy as np

    G, center = _process_params(G, center, dim)
    nNodes = len(G)
    if nNodes == 0:
        return {}

    if dist is None:
        dist = dict(nx.shortest_path_length(G, weight=weight))
    dist_mtx = 1e6 * np.ones((nNodes, nNodes))
    for row, nr in enumerate(G):
        if nr not in dist:
            continue
        rdist = dist[nr]
        for col, nc in enumerate(G):
            if nc not in rdist:
                continue
            dist_mtx[row][col] = rdist[nc]

    if pos is None:
        if dim >= 3:
            pos = random_layout(G, dim=dim)
        elif dim == 2:
            pos = circular_layout(G, dim=dim)
        else:
            pos = {n: pt for n, pt in zip(G, np.linspace(0, 1, len(G)))}
    pos_arr = np.array([pos[n] for n in G])

    pos = _kamada_kawai_solve(dist_mtx, pos_arr, dim)

    pos = rescale_layout(pos, scale=scale) + center
    return dict(zip(G, pos))


def _kamada_kawai_solve(dist_mtx, pos_arr, dim):
    # Anneal node locations based on the Kamada-Kawai cost-function,
    # using the supplied matrix of preferred inter-node distances,
    # and starting locations.

    import numpy as np
    import scipy as sp
    import scipy.optimize  # call as sp.optimize

    meanwt = 1e-3
    costargs = (np, 1 / (dist_mtx + np.eye(dist_mtx.shape[0]) * 1e-3), meanwt, dim)

    optresult = sp.optimize.minimize(
        _kamada_kawai_costfn,
        pos_arr.ravel(),
        method="L-BFGS-B",
        args=costargs,
        jac=True,
    )

    return optresult.x.reshape((-1, dim))


def _kamada_kawai_costfn(pos_vec, np, invdist, meanweight, dim):
    # Cost-function and gradient for Kamada-Kawai layout algorithm
    nNodes = invdist.shape[0]
    pos_arr = pos_vec.reshape((nNodes, dim))

    delta = pos_arr[:, np.newaxis, :] - pos_arr[np.newaxis, :, :]
    nodesep = np.linalg.norm(delta, axis=-1)
    direction = np.einsum("ijk,ij->ijk", delta, 1 / (nodesep + np.eye(nNodes) * 1e-3))

    offset = nodesep * invdist - 1.0
    offset[np.diag_indices(nNodes)] = 0

    cost = 0.5 * np.sum(offset ** 2)
    grad = np.einsum("ij,ij,ijk->ik", invdist, offset, direction) - np.einsum(
        "ij,ij,ijk->jk", invdist, offset, direction
    )

    # Additional parabolic term to encourage mean position to be near origin:
    sumpos = np.sum(pos_arr, axis=0)
    cost += 0.5 * meanweight * np.sum(sumpos ** 2)
    grad += meanweight * sumpos

    return (cost, grad.ravel())


def spectral_layout(G, weight="weight", scale=1, center=None, dim=2):
    """Position nodes using the eigenvectors of the graph Laplacian.

    Using the unnormalized Laplacian, the layout shows possible clusters of
    nodes which are an approximation of the ratio cut. If dim is the number of
    dimensions then the positions are the entries of the dim eigenvectors
    corresponding to the ascending eigenvalues starting from the second one.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.

    weight : string or None   optional (default='weight')
        The edge attribute that holds the numerical value used for
        the edge weight.  If None, then all edge weights are 1.

    scale : number (default: 1)
        Scale factor for positions.

    center : array-like or None
        Coordinate pair around which to center the layout.

    dim : int
        Dimension of layout.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> pos = nx.spectral_layout(G)

    Notes
    -----
    Directed graphs will be considered as undirected graphs when
    positioning the nodes.

    For larger graphs (>500 nodes) this will use the SciPy sparse
    eigenvalue solver (ARPACK).
    """
    # handle some special cases that break the eigensolvers
    import numpy as np

    G, center = _process_params(G, center, dim)

    if len(G) <= 2:
        if len(G) == 0:
            pos = np.array([])
        elif len(G) == 1:
            pos = np.array([center])
        else:
            pos = np.array([np.zeros(dim), np.array(center) * 2.0])
        return dict(zip(G, pos))
    try:
        # Sparse matrix
        if len(G) < 500:  # dense solver is faster for small graphs
            raise ValueError
        A = nx.to_scipy_sparse_array(G, weight=weight, dtype="d")
        # Symmetrize directed graphs
        if G.is_directed():
            A = A + np.transpose(A)
        pos = _sparse_spectral(A, dim)
    except (ImportError, ValueError):
        # Dense matrix
        A = nx.to_numpy_array(G, weight=weight)
        # Symmetrize directed graphs
        if G.is_directed():
            A += A.T
        pos = _spectral(A, dim)

    pos = rescale_layout(pos, scale=scale) + center
    pos = dict(zip(G, pos))
    return pos


def _spectral(A, dim=2):
    # Input adjacency matrix A
    # Uses dense eigenvalue solver from numpy
    import numpy as np

    try:
        nnodes, _ = A.shape
    except AttributeError as err:
        msg = "spectral() takes an adjacency matrix as input"
        raise nx.NetworkXError(msg) from err

    # form Laplacian matrix where D is diagonal of degrees
    D = np.identity(nnodes, dtype=A.dtype) * np.sum(A, axis=1)
    L = D - A

    eigenvalues, eigenvectors = np.linalg.eig(L)
    # sort and keep smallest nonzero
    index = np.argsort(eigenvalues)[1 : dim + 1]  # 0 index is zero eigenvalue
    return np.real(eigenvectors[:, index])


def _sparse_spectral(A, dim=2):
    # Input adjacency matrix A
    # Uses sparse eigenvalue solver from scipy
    # Could use multilevel methods here, see Koren "On spectral graph drawing"
    import numpy as np
    import scipy as sp
    import scipy.sparse  # call as sp.sparse
    import scipy.sparse.linalg  # call as sp.sparse.linalg

    try:
        nnodes, _ = A.shape
    except AttributeError as err:
        msg = "sparse_spectral() takes an adjacency matrix as input"
        raise nx.NetworkXError(msg) from err

    # form Laplacian matrix
    # TODO: Rm csr_array wrapper in favor of spdiags array constructor when available
    D = sp.sparse.csr_array(sp.sparse.spdiags(A.sum(axis=1), 0, nnodes, nnodes))
    L = D - A

    k = dim + 1
    # number of Lanczos vectors for ARPACK solver.What is the right scaling?
    ncv = max(2 * k + 1, int(np.sqrt(nnodes)))
    # return smallest k eigenvalues and eigenvectors
    eigenvalues, eigenvectors = sp.sparse.linalg.eigsh(L, k, which="SM", ncv=ncv)
    index = np.argsort(eigenvalues)[1:k]  # 0 index is zero eigenvalue
    return np.real(eigenvectors[:, index])


def planar_layout(G, scale=1, center=None, dim=2):
    """Position nodes without edge intersections.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G. If G is of type
        nx.PlanarEmbedding, the positions are selected accordingly.

    scale : number (default: 1)
        Scale factor for positions.

    center : array-like or None
        Coordinate pair around which to center the layout.

    dim : int
        Dimension of layout.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node

    Raises
    ------
    NetworkXException
        If G is not planar

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> pos = nx.planar_layout(G)
    """
    import numpy as np

    if dim != 2:
        raise ValueError("can only handle 2 dimensions")

    G, center = _process_params(G, center, dim)

    if len(G) == 0:
        return {}

    if isinstance(G, nx.PlanarEmbedding):
        embedding = G
    else:
        is_planar, embedding = nx.check_planarity(G)
        if not is_planar:
            raise nx.NetworkXException("G is not planar.")
    pos = nx.combinatorial_embedding_to_pos(embedding)
    node_list = list(embedding)
    pos = np.row_stack([pos[x] for x in node_list])
    pos = pos.astype(np.float64)
    pos = rescale_layout(pos, scale=scale) + center
    return dict(zip(node_list, pos))


def spiral_layout(G, scale=1, center=None, dim=2, resolution=0.35, equidistant=False):
    """Position nodes in a spiral layout.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.
    scale : number (default: 1)
        Scale factor for positions.
    center : array-like or None
        Coordinate pair around which to center the layout.
    dim : int, default=2
        Dimension of layout, currently only dim=2 is supported.
        Other dimension values result in a ValueError.
    resolution : float, default=0.35
        The compactness of the spiral layout returned.
        Lower values result in more compressed spiral layouts.
    equidistant : bool, default=False
        If True, nodes will be positioned equidistant from each other
        by decreasing angle further from center.
        If False, nodes will be positioned at equal angles
        from each other by increasing separation further from center.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node

    Raises
    ------
    ValueError
        If dim != 2

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> pos = nx.spiral_layout(G)

    References
    ----------
    .. [1] Se-Hang Cheong, Yain-Whar Si
       "Force-directed algorithms for schematic drawings and placement: A survey",
       [2019]
       https://journals.sagepub.com/doi/full/10.1177/1473871618821740

    .. [2] 
       https://journals.sagepub.com/doi/full/10.1177/1473871618821740


    Notes
    -----
    This algorithm currently only works in two dimensions.

    """
    import numpy as np

    if dim != 2:
        raise ValueError("can only handle 2 dimensions")

    G, center = _process_params(G, center, dim)

    if len(G) == 0:
        return {}
    if len(G) == 1:
        return {nx.utils.arbitrary_element(G): center}

    pos = []
    if equidistant:
        chord = 1
        step = 0.5
        theta = resolution
        theta += chord / (step * theta)
        for _ in range(len(G)):
            r = step * theta
            theta += chord / r
            pos.append([np.cos(theta) * r, np.sin(theta) * r])

    else:
        dist = np.arange(len(G), dtype=float)
        angle = resolution * dist
        pos = np.transpose(dist * np.array([np.cos(angle), np.sin(angle)]))

    pos = rescale_layout(np.array(pos), scale=scale) + center

    pos = dict(zip(G, pos))

    return pos


def multipartite_layout(G, subset_key="subset", align="vertical", scale=1, center=None):
    """Position nodes in layers of straight lines.

    Parameters
    ----------
    G : NetworkX graph or list of nodes
        A position will be assigned to every node in G.

    subset_key : string (default='subset')
        Key of node data to be used as layer subset.

    align : string (default='vertical')
        The alignment of nodes. Vertical or horizontal.

    scale : number (default: 1)
        Scale factor for positions.

    center : array-like or None
        Coordinate pair around which to center the layout.

    Returns
    -------
    pos : dict
        A dictionary of positions keyed by node.

    Examples
    --------
    >>> G = nx.complete_multipartite_graph(28, 16, 10)
    >>> pos = nx.multipartite_layout(G)

    Notes
    -----
    This algorithm currently only works in two dimensions and does not
    try to minimize edge crossings.

    Network does not need to be a complete multipartite graph. As long as nodes
    have subset_key data, they will be placed in the corresponding layers.

    """
    import numpy as np

    if align not in ("vertical", "horizontal"):
        msg = "align must be either vertical or horizontal."
        raise ValueError(msg)

    G, center = _process_params(G, center=center, dim=2)
    if len(G) == 0:
        return {}

    layers = {}
    for v, data in G.nodes(data=True):
        try:
            layer = data[subset_key]
        except KeyError:
            msg = "all nodes must have subset_key (default='subset') as data"
            raise ValueError(msg)
        layers[layer] = [v] + layers.get(layer, [])

    pos = None
    nodes = []

    width = len(layers)
    for i, layer in enumerate(layers.values()):
        height = len(layer)
        xs = np.repeat(i, height)
        ys = np.arange(0, height, dtype=float)
        offset = ((width - 1) / 2, (height - 1) / 2)
        layer_pos = np.column_stack([xs, ys]) - offset
        if pos is None:
            pos = layer_pos
        else:
            pos = np.concatenate([pos, layer_pos])
        nodes.extend(layer)
    pos = rescale_layout(pos, scale=scale) + center
    if align == "horizontal":
        pos = np.flip(pos, 1)
    pos = dict(zip(nodes, pos))
    return pos


def rescale_layout(pos, scale=1):
    """Returns scaled position array to (-scale, scale) in all axes.

    The function acts on NumPy arrays which hold position information.
    Each position is one row of the array. The dimension of the space
    equals the number of columns. Each coordinate in one column.

    To rescale, the mean (center) is subtracted from each axis separately.
    Then all values are scaled so that the largest magnitude value
    from all axes equals `scale` (thus, the aspect ratio is preserved).
    The resulting NumPy Array is returned (order of rows unchanged).

    Parameters
    ----------
    pos : numpy array
        positions to be scaled. Each row is a position.

    scale : number (default: 1)
        The size of the resulting extent in all directions.

    Returns
    -------
    pos : numpy array
        scaled positions. Each row is a position.

    See Also
    --------
    rescale_layout_dict
    """
    # Find max length over all dimensions
    lim = 0  # max coordinate for all axes
    for i in range(pos.shape[1]):
        pos[:, i] -= pos[:, i].mean()
        lim = max(abs(pos[:, i]).max(), lim)
    # rescale to (-scale, scale) in all directions, preserves aspect
    if lim > 0:
        for i in range(pos.shape[1]):
            pos[:, i] *= scale / lim
    return pos


def rescale_layout_dict(pos, scale=1):
    """Return a dictionary of scaled positions keyed by node

    Parameters
    ----------
    pos : A dictionary of positions keyed by node

    scale : number (default: 1)
        The size of the resulting extent in all directions.

    Returns
    -------
    pos : A dictionary of positions keyed by node

    Examples
    --------
    >>> import numpy as np
    >>> pos = {0: np.array((0, 0)), 1: np.array((1, 1)), 2: np.array((0.5, 0.5))}
    >>> nx.rescale_layout_dict(pos)
    {0: array([-1., -1.]), 1: array([1., 1.]), 2: array([0., 0.])}

    >>> pos = {0: np.array((0, 0)), 1: np.array((-1, 1)), 2: np.array((-0.5, 0.5))}
    >>> nx.rescale_layout_dict(pos, scale=2)
    {0: array([ 2., -2.]), 1: array([-2.,  2.]), 2: array([0., 0.])}

    See Also
    --------
    rescale_layout
    """
    import numpy as np

    if not pos:  # empty_graph
        return {}
    pos_v = np.array(list(pos.values()))
    pos_v = rescale_layout(pos_v, scale=scale)
    return dict(zip(pos, pos_v))
