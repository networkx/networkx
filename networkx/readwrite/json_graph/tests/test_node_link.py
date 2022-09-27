import copy
import json

import pytest

import networkx as nx
from networkx.readwrite.json_graph import node_link_data, node_link_graph
from networkx.utils import graphs_equal


# TODO: To be removed when signature change complete
def test_attrs_deprecation(recwarn):
    G = nx.path_graph(3)

    # No warnings when `attrs` kwarg not used
    data = node_link_data(G)
    H = node_link_graph(data)
    assert len(recwarn) == 0

    # Future warning raised with `attrs` kwarg
    attrs = dict(source="source", target="target", name="id", key="key", link="links")
    data = node_link_data(G, attrs=attrs)
    assert len(recwarn) == 1

    recwarn.clear()
    H = node_link_graph(data, attrs=attrs)
    assert len(recwarn) == 1


class TestNodeLink:

    # TODO: To be removed when signature change complete
    def test_custom_attrs_dep(self):
        G = nx.path_graph(4)
        G.add_node(1, color="red")
        G.add_edge(1, 2, width=7)
        G.graph[1] = "one"
        G.graph["foo"] = "bar"

        attrs = dict(
            source="c_source",
            target="c_target",
            name="c_id",
            key="c_key",
            link="c_links",
        )

        H = node_link_graph(
            node_link_data(G, attrs=attrs), multigraph=False, attrs=attrs
        )
        assert graphs_equal(G, H)
        assert H.graph["foo"] == "bar"
        assert H.nodes[1]["color"] == "red"
        assert H[1][2]["width"] == 7

        # provide only a partial dictionary of keywords.
        # This is similar to an example in the doc string
        attrs = dict(
            link="c_links",
            source="c_source",
            target="c_target",
        )
        H = node_link_graph(
            node_link_data(G, attrs=attrs), multigraph=False, attrs=attrs
        )
        assert nx.is_isomorphic(G, H)
        assert H.graph["foo"] == "bar"
        assert H.nodes[1]["color"] == "red"
        assert H[1][2]["width"] == 7

    # TODO: To be removed when signature change complete
    def test_exception_dep(self):
        with pytest.raises(nx.NetworkXError):
            G = nx.MultiDiGraph()
            attrs = dict(name="node", source="node", target="node", key="node")
            node_link_data(G, attrs)

    def test_graph(self):
        G = nx.path_graph(4)
        H = node_link_graph(node_link_data(G))
        assert graphs_equal(G, H)

    def test_input_data_is_not_modified_when_building_graph(self):
        G = nx.path_graph(4)
        input_data = node_link_data(G)
        orig_data = copy.deepcopy(input_data)
        # Ensure input is unmodified by deserialisation
        node_link_graph(input_data)
        assert input_data == orig_data

    def test_graph_attributes(self):
        G = nx.path_graph(4)
        G.add_node(1, color="red")
        G.add_edge(1, 2, width=7)
        G.graph[1] = "one"
        G.graph["foo"] = "bar"

        H = node_link_graph(node_link_data(G))
        assert H.graph["foo"] == "bar"
        assert H.nodes[1]["color"] == "red"
        assert H[1][2]["width"] == 7
        assert graphs_equal(G, H)

        d = json.dumps(node_link_data(G))
        H = node_link_graph(json.loads(d))
        assert H.graph["foo"] == "bar"
        assert H.nodes[1]["color"] == "red"
        assert H[1][2]["width"] == 7
        assert nx.is_isomorphic(G, H)

    def test_digraph(self):
        G = nx.DiGraph()
        H = node_link_graph(node_link_data(G))
        assert H.is_directed()
        assert graphs_equal(G, H)
        assert isinstance(G, nx.DiGraph)

    def test_multigraph(self):
        G = nx.MultiGraph()
        G.add_edge(1, 2, key="first")
        G.add_edge(1, 2, key="second", color="blue")
        H = node_link_graph(node_link_data(G))
        assert graphs_equal(G, H)
        assert isinstance(G, nx.MultiGraph)
        assert H[1][2]["second"]["color"] == "blue"

    def test_graph_with_tuple_nodes(self):
        G = nx.Graph()
        G.add_edge((0, 0), (1, 0), color=[255, 255, 0])
        d = node_link_data(G)
        dumped_d = json.dumps(d)
        dd = json.loads(dumped_d)
        H = node_link_graph(dd)
        assert H.nodes[(0, 0)] == G.nodes[(0, 0)]
        assert H[(0, 0)][(1, 0)]["color"] == [255, 255, 0]
        assert graphs_equal(G, H)

    def test_unicode_keys(self):
        q = "qualité"
        G = nx.Graph()
        G.add_node(1, **{q: q})
        s = node_link_data(G)
        output = json.dumps(s, ensure_ascii=False)
        data = json.loads(output)
        H = node_link_graph(data)
        assert H.nodes[1][q] == q
        assert graphs_equal(G, H)

    def test_exception(self):
        with pytest.raises(nx.NetworkXError):
            G = nx.MultiDiGraph()
            attrs = dict(name="node", source="node", target="node", key="node")
            node_link_data(G, **attrs)

    def test_string_ids(self):
        q = "qualité"
        G = nx.DiGraph()
        G.add_node("A")
        G.add_node(q)
        G.add_edge("A", q)
        H = node_link_graph(node_link_data(G))
        assert graphs_equal(G, H)

    def test_custom_attrs(self):
        G = nx.path_graph(4)
        G.add_node(1, color="red")
        G.add_edge(1, 2, width=7)
        G.graph[1] = "one"
        G.graph["foo"] = "bar"

        attrs = dict(
            source="c_source",
            target="c_target",
            name="c_id",
            key="c_key",
            link="c_links",
        )

        H = node_link_graph(node_link_data(G, **attrs), multigraph=False, **attrs)
        assert graphs_equal(G, H)
        assert H.graph["foo"] == "bar"
        assert H.nodes[1]["color"] == "red"
        assert H[1][2]["width"] == 7
