import networkx.algorithms.thesis_Alex.utils.utils as u
import networkx.algorithms.thesis_Alex.utils.graphs as g


if __name__ == '__main__':
    new_edge = ('3', '6')
    G_1 = g.g_1()

    u.compare_kourtellis_bc(G_1, new_edge)


