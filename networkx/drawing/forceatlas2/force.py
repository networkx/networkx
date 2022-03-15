__author__ = "Casper van Elteren"
__info__ = "Native networkx implementation for networkx"
import networkx as nx, numpy as np
from math import sqrt

# define Moore neighborhood


class Graph:
    def __init__(self, g, gpos, settings):
        """
        Convenience class for speeding up the code with cython.
        This offers no speed gains for native python code.
        It is recommended for the user to install cython for
        runtime speed gains.
        """
        self.settings = settings
        n = len(g)
        self.number_of_nodes = n
        # setup buffers
        self.pos = np.zeros((n, 2))
        self.change = np.zeros((n, 2))
        self.mass = np.zeros(n)
        self.size = np.zeros(n)
        self.edges = {}

        # assign positions
        e = {}
        for node, p in gpos.items():
            self.pos[node, 0] = p[0]
            self.pos[node, 1] = p[1]
            self.mass[node] = g.nodes[node].get("mass", g.degree(node) + 1)
            self.size[node] = g.nodes[node].get("size", 1.0)
            e[node] = {}

        # make edges
        for x, y, d in g.edges(data=True):
            # if x >= y:
            #     break
            e[x][y] = d.get("weight", 1)
            if not g.is_directed():
                e[y][x] = d.get("weight", 1)
        self.edges = e


def get_mass(node, g):
    return g.mass[node]


def get_size(node, g):
    return g.size[node]


def get_pos(node, g):
    return g.pos[node]


def get_change(node, g):
    # get update at simulation step
    return g.change[node]


def get_difference(x, y, g):
    # Simple difference
    out = np.zeros(2)
    x_pos = get_pos(x, g)
    y_pos = get_pos(y, g)
    for idx in range(2):
        out[idx] = x_pos[idx] - y_pos[idx]
    return out


def get_distance(x, y, g, use_weight=False):
    # Euclidean distance
    d = 0
    delta = get_difference(x, y, g)
    for idx in range(2):
        d += delta[idx] * delta[idx]
    if use_weight:
        return sqrt(d) * g.edges[x][y] ** g.settings.edge_weight
    else:
        return sqrt(d)


def update(node, value, g):
    g.change[node][0] += value[0]
    g.change[node][1] += value[1]


def linear_attraction(x, y, g, k):
    # apply attraction
    dist = get_distance(x, y, g, use_weight=True)
    if g.settings.distributed_action:
        k /= get_mass(x, g)

    value = get_difference(x, y, g)
    value[0] *= -k
    value[1] *= -k
    if g.settings.dissuade_hubs:
        value[0] /= get_mass(x, g)
        value[1] /= get_mass(x, g)
    # update x
    update(x, value, g)

    # # update y
    value[0] *= -1
    value[1] *= -1
    update(y, value, g)


def linear_repulsion(x, y, g, k):
    d = get_distance(x, y, g)
    if d == 0.0:
        return
    if g.settings.prevent_overlap:
        d_ = d - get_size(x, g) - get_size(y, g)
        if d_ > 0:
            d = d_
    factor = k * get_mass(x, g) * get_mass(y, g) / (d * d)

    # get difference
    delta = get_difference(x, y, g)
    delta[0] *= factor
    delta[1] *= factor
    update(x, delta, g)

    delta[0] *= -1
    delta[1] *= -1
    update(y, delta, g)


def linlog_attraction(x, y, g, k):
    dist = get_distance(x, y, g, use_weight=True) / get_mass(x, g)
    if dist == 0:
        return
    value = get_difference(x, y, g)
    value[0] *= -k * np.log(1 + dist) / dist
    value[1] *= -k * np.log(1 + dist) / dist

    if g.settings.distributed_action:
        value[0] /= get_mass(x, g)
        value[1] /= get_mass(y, g)
    update(x, value, g)


def apply_attraction(
    node,
    g,
    attraction,
    k,
):
    # apply force in place
    for neighbor in g.edges[node].keys():
        attraction(
            node,
            neighbor,
            g,
            k=k,
        )


def apply_repulsion(node, g, repulsion, k=1.0):
    # get discreteized nearest neighbors
    # apply linear force
    current_pos = get_pos(node, g)
    for other in range(g.number_of_nodes):
        if other >= node:
            return
        repulsion(node, other, g, k=k)


def apply_gravity(node, g, k=1):
    # attract nodes to center (0,0)
    # setting strong may result in a large pull
    pos = get_pos(node, g)
    d = sqrt(pos[0] ** 2 + pos[1] ** 2)
    # skip to provent zero division
    if d == 0:
        return
    value = np.zeros(2)
    value[0] = -k * get_mass(node, g) * pos[0] / d
    value[1] = -k * get_mass(node, g) * pos[1] / d
    if g.settings.strong_gravity:
        pos[0] *= d
        pos[1] *= d
    update(node, value, g)


class Swing:
    def __init__(self, swing=0.0, effective_traction=0.0):
        self.swing = swing
        self.effective_traction = effective_traction


# function deduced from original java code
def apply_forces(g, swing, speed, speed_efficiency, jitter_tolerance) -> tuple:
    # adjust speed and apply forces

    # from javacode; a bit opague as to what this exactly does
    # see paper for more info
    n = g.number_of_nodes
    estimated_jitter_tolerance = 0.05 * np.sqrt(n)
    min_jitter = np.sqrt(estimated_jitter_tolerance)
    max_jitter = 10

    tmp = estimated_jitter_tolerance * swing.effective_traction / (n**2)
    jitter = jitter_tolerance * max(min_jitter, min(max_jitter, tmp))

    min_speed_efficiency = 0.05
    if swing.swing / swing.effective_traction > 2.0:
        if speed_efficiency > min_speed_efficiency:
            speed_efficiency *= 0.5
        jitter = max(jitter, jitter_tolerance)

    if swing.swing == 0:
        target_speed = np.inf
    else:
        z = swing.effective_traction / swing.swing
        target_speed = jitter * speed_efficiency * z

    if swing.swing > jitter * swing.effective_traction:
        if speed_efficiency > min_speed_efficiency:
            speed_efficiency *= 0.7
    elif speed < 1000:
        speed_efficiency *= 1.3

    maxRise = 0.5
    speed += min(target_speed - speed, maxRise * speed)

    # update positions
    for node in range(n):
        pos = get_pos(node, g)
        change = get_change(node, g)

        swinging = get_mass(node, g) * np.sqrt(
            (pos[0] - change[0]) ** 2 + (pos[1] - change[1]) ** 2
        )
        factor = speed / (1.0 + np.sqrt(speed * swinging))

        g.pos[node][0] += change[0] * factor
        g.pos[node][1] += change[1] * factor
        change[0] = 0
        change[1] = 0

    return speed, speed_efficiency


class Settings:
    def __init__(
        self,
        jitter_tolerance=1.0,
        scaling=2.0,
        distributed_action=False,
        strong_gravity=False,
        prevent_overlap=False,
        dissuade_hubs=False,
        edge_weight=False,
        linlog=False,
    ):
        """Settings object for ForceAtlas2

        See [1] for more info on the parameters

        [1]: https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0098679&type=printable
        Parameters
        ----------
        jitter_tolerance : float
            Jitter  tolerance  for  adjusting  speed  of  layout
            generation
        scaling : float
            Controls  force scaling  constants k_attraction  and
            k_repulsion
        distributed_action : bool
        strong_gravity : bool
            Controls the  "pull" to  the center  of mass  of the
            plot (0,0)
        prevent_overlap : bool
            Prevent node overlapping in the layout
        dissuade_hubs : bool
            Prevent hub clustering
        edge_weight : bool
            Generate layout with or without considering the edge
            weights
        linlog : bool
            Use log attraction rather than linear attraction
        """
        self.jitter_tolerance = jitter_tolerance
        self.scaling = scaling
        self.distributed_action = distributed_action
        self.strong_gravity = strong_gravity
        self.prevent_overlap = prevent_overlap
        self.dissuade_hubs = dissuade_hubs
        self.edge_weight = edge_weight
        self.linlog = linlog

    def __repr__(self):
        # fancy print settings
        s = "\n"
        for k, v in self.__dict__.items():
            if not hasattr(v, "__call__"):
                s += f"{k}:\t {v}\n"
        return s


def forceatlas2(
    g: nx.Graph,
    pos=None,
    n_iter=200,
    settings=Settings(),
) -> dict:
    """ForceAtlas2 implementation in networkx

    ForceAtlas2         network          layout         from
    https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0098679

    Parameters
    ----------
    g : nx.Graph
        Networkx graph
    pos : dict
        Networkx position layout
    n_iter : int
        Number of simulation steps
    settings : Settings
        Settings for ForceAtlas2 simulation

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.florentine_family_graph()
    >>> nx.draw(G, pos = nx.forceatlas2_layout(G))
    """

    g = nx.convert_node_labels_to_integers(g, label_attribute="orig")
    print(f"Using {settings=}")
    if pos is None:
        print("Initializing random coordinates")
        pos = nx.random_layout(g)
    else:
        pos = {node: pos[g.nodes[node]["orig"]] for node in g.nodes()}

    G = Graph(g, pos, settings)

    # setup position and change vectors
    # deepcopy is not on ndarray(!)
    nx.set_node_attributes(g, {node: p.copy() for node, p in pos.items()}, "pos")
    nx.set_node_attributes(
        g, {node: np.zeros(p.size) for node, p in pos.items()}, "change"
    )

    # construct dpos
    # dpos = make_discrete_coordinates(pos)
    nodes = np.asarray(g.nodes())

    # init speed and effiency
    speed = 1.0
    speed_efficiency = 1.0

    from tqdm import tqdm

    attraction_force = linear_attraction
    if settings.linlog:
        attraction_force = linlog_attraction
    repulsion_force = linear_repulsion
    swing = Swing(1, 1)
    for i in tqdm(range(n_iter)):
        # get rid of order effect
        speed, speed_efficiency = apply_forces(
            G,
            swing,
            speed=speed,
            speed_efficiency=speed_efficiency,
            jitter_tolerance=settings.jitter_tolerance,
        )
        # print(f"{speed=} {speed_efficiency=}")
        for node in nodes:

            # order effect?
            apply_repulsion(
                node,
                G,
                repulsion=repulsion_force,
                k=settings.scaling,
            )

            apply_gravity(node, G, k=1.0)

            apply_attraction(
                node,
                G,
                attraction=attraction_force,
                k=1.0,
            )

            node_pos = G.pos[node]
            change = G.change[node]
            swinging = np.sqrt(
                (node_pos[0] - change[0]) ** 2 + (node_pos[1] - change[1]) ** 2
            )
            swing.swing += get_mass(node, G) * swinging
            swing.effective_traction += (
                0.5
                * get_mass(node, G)
                * np.sqrt(
                    (node_pos[0] + change[0]) ** 2 + (node_pos[1] + change[1]) ** 2
                )
            )

    pos = {g.nodes[node]["orig"]: G.pos[node] for node in g.nodes()}
    return pos


try:
    import cython

    if not cython.compiled:
        print(f"Warning {__file__} is not compiled")
except:
    print(f"Warning {__file__} is not compiled, consider installing cython")
