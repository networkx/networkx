from . import isomorphVF2pp as vf2pp


class GraphMatcher(vf2pp.GraphMatcher):
    def __init__(self, G1, G2, check_labels=False):
        vf2pp.GraphMatcher.__init__(self, G1, G2)

        if not check_labels:
            self.node_labels = None
        else:
            self.node_labels = dict()
            # todo: Create dictionary with node-label as key-value pair.
