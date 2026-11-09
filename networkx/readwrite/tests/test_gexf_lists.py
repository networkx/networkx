import io
from copy import deepcopy
from decimal import Decimal
from xml.etree.ElementTree import fromstring
from xml.sax.saxutils import escape, quoteattr

import pytest

import networkx as nx


def list_document(attribute_type, value, default=None, dynamic=False, scope="node"):
    mode = "dynamic" if dynamic else "static"
    default_xml = "" if default is None else f"<default>{escape(default)}</default>"
    times = ' start="0" end="1"' if dynamic else ""
    values = (
        f'<attvalues><attvalue for="0" value={quoteattr(value)}{times}/></attvalues>'
    )
    node_values = values if scope == "node" else ""
    edge_values = values if scope == "edge" else ""
    return io.BytesIO(
        f"""<gexf xmlns="http://gexf.net/1.3" version="1.3">
          <graph defaultedgetype="directed" mode="{mode}" timeformat="integer">
            <attributes class="{scope}" mode="{mode}">
              <attribute id="0" title="values" type="{attribute_type}">
                {default_xml}
              </attribute>
            </attributes>
            <nodes><node id="a">{node_values}</node><node id="b"/></nodes>
            <edges><edge source="a" target="b">{edge_values}</edge></edges>
          </graph>
        </gexf>""".encode()
    )


@pytest.mark.parametrize("scope", ["node", "edge"])
@pytest.mark.parametrize("dynamic", [False, True])
@pytest.mark.parametrize(
    ("attribute_type", "value", "expected"),
    [
        ("liststring", "[dance, ski]", ["dance", "ski"]),
        ("liststring", "['two words', \"a,b\", '']", ["two words", "a,b", ""]),
        ("liststring", r'["a\\b", "a\"b", "a\nb"]', ["a\\b", 'a"b', "a\nb"]),
        ("listboolean", "[true, false, 1, 0]", [True, False, True, False]),
        ("listinteger", "[1, -2, 3]", [1, -2, 3]),
        ("listlong", "[1, 9223372036854775807]", [1, 9223372036854775807]),
        (
            "listbiginteger",
            "[123456789012345678901234567890]",
            [123456789012345678901234567890],
        ),
        ("listbyte", "[-128, 127]", [-128, 127]),
        ("listshort", "[-32768, 32767]", [-32768, 32767]),
        ("listfloat", "[1.25, -2e-3]", [1.25, -0.002]),
        ("listdouble", "[1.25, -2e-3]", [1.25, -0.002]),
        (
            "listbigdecimal",
            "[0.1234567890123456789]",
            [Decimal("0.1234567890123456789")],
        ),
        ("listchar", "['x', 'λ']", ["x", "λ"]),
        ("listinteger", "[]", []),
        ("liststring", "[  ]", []),
        ("liststring", "", []),
        ("liststring", r'["\ud83d\ude00"]', ["😀"]),
    ],
)
def test_read_list_attribute(scope, dynamic, attribute_type, value, expected):
    graph = nx.read_gexf(
        list_document(attribute_type, value, dynamic=dynamic, scope=scope)
    )
    actual = graph.nodes["a"] if scope == "node" else graph.edges["a", "b"]
    assert actual["values"] == ([(expected, 0, 1)] if dynamic else expected)


@pytest.mark.parametrize("scope", ["node", "edge"])
@pytest.mark.parametrize(
    ("attribute_type", "default", "expected"),
    [
        ("listinteger", "[1, 2]", [1, 2]),
        ("listboolean", "[true, false]", [True, False]),
        ("liststring", "['a,b', 'λ']", ["a,b", "λ"]),
        ("listdouble", "[]", []),
    ],
)
def test_read_list_default(scope, attribute_type, default, expected):
    graph = nx.read_gexf(
        list_document(attribute_type, "[]", default=default, scope=scope)
    )
    assert graph.graph[f"{scope}_default"] == {"values": expected}


@pytest.mark.parametrize(
    "graph_type", [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
)
@pytest.mark.parametrize(
    ("values", "attribute_type"),
    [
        ([1, 2, -3], "listlong"),
        ([True, False], "listboolean"),
        ([0.25, 2.5], "listdouble"),
        ([Decimal("0.1234567890123456789")], "listbigdecimal"),
        (
            ["a,b", " leading and trailing ", "", "λ", 'a"b', "a\\b", "a\nb"],
            "liststring",
        ),
        ([], "liststring"),
    ],
)
def test_list_roundtrip(graph_type, values, attribute_type):
    graph = graph_type()
    graph.add_node("a", values=values)
    graph.add_node("b")
    graph.add_edge("a", "b", values=values)
    original = deepcopy(graph)
    stream = io.BytesIO()
    nx.write_gexf(graph, stream, version="1.3")
    root = fromstring(stream.getvalue())
    ns = {"g": "http://gexf.net/1.3"}
    declarations = [
        attribute
        for attribute in root.findall("g:graph/g:attributes/g:attribute", ns)
        if attribute.get("title") == "values"
    ]
    assert [attribute.get("type") for attribute in declarations] == [attribute_type] * 2
    stream.seek(0)
    result = nx.read_gexf(stream)
    assert result.nodes["a"]["values"] == values
    assert next(iter(result.edges(data=True)))[2]["values"] == values
    assert result.graph["mode"] == "static"
    assert nx.utils.graphs_equal(graph, original)


@pytest.mark.parametrize("empty_first", [False, True])
@pytest.mark.parametrize("scope", ["node", "edge"])
def test_empty_list_infers_type_from_other_values(scope, empty_first):
    graph = nx.path_graph(["a", "b", "c"])
    attributes = (
        list(graph.nodes.values()) if scope == "node" else list(graph.edges.values())
    )
    first, second = ([], [1, 2]) if empty_first else ([1, 2], [])
    attributes[0]["values"] = first
    attributes[1]["values"] = second
    stream = io.BytesIO()
    nx.write_gexf(graph, stream, version="1.3")
    stream.seek(0)
    result = nx.read_gexf(stream)
    actual = (
        list(result.nodes.values()) if scope == "node" else list(result.edges.values())
    )
    assert actual[0]["values"] == first
    assert actual[1]["values"] == second


def test_list_default_roundtrip():
    graph = nx.Graph()
    graph.graph["node_default"] = {"values": [1, 2]}
    graph.graph["edge_default"] = {"values": [False, True]}
    graph.add_node("a", values=[])
    graph.add_edge("a", "b", values=[])
    stream = io.BytesIO()
    nx.write_gexf(graph, stream, version="1.3")
    stream.seek(0)
    result = nx.read_gexf(stream)
    assert result.graph["node_default"] == graph.graph["node_default"]
    assert result.graph["edge_default"] == graph.graph["edge_default"]
    assert result.nodes["a"]["values"] == []
    assert result.edges["a", "b"]["values"] == []


@pytest.mark.parametrize("version", ["1.1draft", "1.2draft", "1.3"])
def test_dynamic_scalar_attributes_keep_their_representation(version):
    graph = nx.Graph()
    graph.add_node("a", changing=[(True, 0, 1), (False, 1, 2)], fixed=42)
    stream = io.BytesIO()
    nx.write_gexf(graph, stream, version=version)
    stream.seek(0)
    result = nx.read_gexf(stream)
    assert result.nodes["a"]["changing"] == [(True, 0, 1), (False, 1, 2)]
    assert result.nodes["a"]["fixed"] == 42


def test_dynamic_list_roundtrip():
    graph = nx.Graph()
    values = [([], 0, 1), ([1, 2], 1, 2)]
    graph.add_node("a", values=values, fixed=["one", "two"])
    stream = io.BytesIO()
    nx.write_gexf(graph, stream, version="1.3")
    stream.seek(0)
    result = nx.read_gexf(stream)
    assert result.nodes["a"]["values"] == values
    assert result.nodes["a"]["fixed"] == ["one", "two"]


@pytest.mark.parametrize("version", ["1.1draft", "1.2draft"])
def test_legacy_liststring_stays_a_string(version):
    namespace = nx.readwrite.gexf.GEXF.versions[version]["NS_GEXF"]
    document = list_document("liststring", "foo;bar").getvalue()
    document = document.replace(b"http://gexf.net/1.3", namespace.encode())
    graph = nx.read_gexf(io.BytesIO(document), version=version)
    assert graph.nodes["a"]["values"] == "foo;bar"


@pytest.mark.parametrize("values", [[1, "a"], [True, 1], [[1, 2]], [object()]])
def test_unsupported_list_values(values):
    graph = nx.Graph()
    graph.add_node("a", values=values)
    with pytest.raises(TypeError, match="list attribute"):
        next(nx.generate_gexf(graph, version="1.3"))


def test_list_type_conflict():
    graph = nx.Graph()
    graph.add_node("a", values=[1])
    graph.add_node("b", values=["a"])
    with pytest.raises(ValueError, match="values"):
        list(nx.generate_gexf(graph, version="1.3"))


@pytest.mark.parametrize(
    "first, second", [("abc", ["a"]), (["a"], "abc"), (1, [1]), ([1], 1)]
)
def test_list_and_scalar_type_conflict(first, second):
    graph = nx.Graph()
    graph.add_node("a", values=first)
    graph.add_node("b", values=second)
    with pytest.raises(ValueError, match="values"):
        list(nx.generate_gexf(graph, version="1.3"))


def test_dynamic_list_and_scalar_type_conflict():
    graph = nx.Graph()
    graph.add_node("a", values=[([1, 2], 0, 1), ("abc", 1, 2)])
    with pytest.raises(ValueError, match="values"):
        list(nx.generate_gexf(graph, version="1.3"))


@pytest.mark.parametrize(
    "value", ["not a list", "[1,]", "[1,,2]", "['unterminated]", "[ , 1]"]
)
def test_invalid_list_syntax(value):
    with pytest.raises(ValueError, match="GEXF list value"):
        nx.read_gexf(list_document("liststring", value))


def test_list_nonfinite_float_roundtrip():
    graph = nx.Graph()
    graph.add_node("a", values=[float("inf"), float("-inf"), float("nan")])
    stream = io.BytesIO()
    nx.write_gexf(graph, stream, version="1.3")
    assert b"[INF, -INF, NaN]" in stream.getvalue()
    stream.seek(0)
    values = nx.read_gexf(stream).nodes["a"]["values"]
    assert values[:2] == [float("inf"), float("-inf")]
    assert values[2] != values[2]


def test_generate_list_attribute():
    graph = nx.Graph()
    graph.add_node("a", values=[1, 2])
    document = "\n".join(nx.generate_gexf(graph, version="1.3"))
    assert nx.read_gexf(io.BytesIO(document.encode())).nodes["a"]["values"] == [1, 2]


def test_list_attribute_with_hierarchy():
    graph = nx.Graph()
    graph.add_node("parent", values=[1])
    graph.add_node("child", parents=["parent"], values=[2])
    stream = io.BytesIO()
    nx.write_gexf(graph, stream, version="1.3")
    stream.seek(0)
    result = nx.read_gexf(stream)
    assert result.nodes["child"]["parents"] == ["parent"]
    assert result.nodes["child"]["values"] == [2]


def test_list_default_type_conflict():
    graph = nx.Graph()
    graph.graph["node_default"] = {"values": "abc"}
    graph.add_node("a", values=[])
    with pytest.raises(ValueError, match="values"):
        list(nx.generate_gexf(graph, version="1.3"))


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_decimal_list(value):
    graph = nx.Graph()
    graph.add_node("a", values=[Decimal(value)])
    with pytest.raises(ValueError, match="Non-finite decimal"):
        list(nx.generate_gexf(graph, version="1.3"))


@pytest.mark.parametrize("extension", ["gexf", "gexf.gz", "gexf.bz2"])
def test_list_file_roundtrip(tmp_path, extension):
    graph = nx.Graph()
    graph.add_node("a", values=["a,b", "λ"])
    path = tmp_path / f"graph.{extension}"
    nx.write_gexf(graph, path, version="1.3")
    assert nx.read_gexf(path).nodes["a"]["values"] == ["a,b", "λ"]
