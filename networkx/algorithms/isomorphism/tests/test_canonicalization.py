import random
import time

import pytest

import networkx as nx
from networkx.algorithms import isomorphism as iso


def Carhart_Fig1():
    "Figure 1 from https://doi.org/10.1021/ci60014a015"
    return [
        "1 2",
        "6 1",
        "8 1",
        "2 3",
        "8 2",
        "3 4",
        "10 3",
        "4 5",
        "10 4",
        "5 6",
        "9 5",
        "9 6",
        "7 8",
        "9 7",
        "7 10",
    ]


def Carhart_Fig2():
    "Figure 2 from https://doi.org/10.1021/ci60014a015"
    return [
        "1 2",
        "6 1",
        "1 8",
        "2 3",
        "7 2",
        "3 4",
        "4 5",
        "7 4",
        "5 6",
        "5 9",
        "10 8",
        "9 11",
        "10 11",
        "12 10",
        "11 12",
    ]


def Carhart_Fig4():
    "Figure 4 from https://doi.org/10.1021/ci60014a015"
    return [
        "1 2",
        "1 6",
        "2 3",
        "3 4",
        "8 3",
        "4 5",
        "5 7",
        "6 7",
        "8 6",
        "8 7",
        "9 8",
        "9 10",
        "13 9",
        "9 14",
        "10 11",
        "10 13",
        "11 12",
        "12 13",
        "14 15",
        "16 14",
        "15 16",
    ]


def Schneider_Fig4c():
    "Figure 4c from https://doi.org/10.1021/acs.jcim.5b00543"
    return [
        "1 2",
        "1 3",
        "2 4",
        "3 4",
        "4 5",
        "2 6",
        "1 7",
        "3 8",
        "5 9",
        "8 10",
        "7 11",
        "6 12",
        "10 7",
        "11 6",
        "12 5",
        "9 8",
        "12 13",
        "9 14",
        "10 15",
        "11 16",
        "13 14",
        "14 15",
        "15 16",
        "16 13",
    ]


def Krotko_Fig1():
    "Figure 1 from https://doi.org/10.1186/s13321-020-00453-4"
    return [
        "1 2",
        "2 3",
        "1 4",
        "3 5",
        "3 6",
        "4 7",
        "4 8",
        "8 9",
        "7 10",
        "5 11",
        "6 12",
        "11 13",
        "12 13",
        "10 14",
        "9 14",
        "14 15",
        "15 16",
        "16 13",
    ]


def Krotko_Fig2():
    "Figure 2 from https://doi.org/10.1186/s13321-020-00453-4"
    return [
        "1 2",
        "1 3",
        "1 4",
        "4 3",
        "3 5",
        "4 5",
        "2 6",
        "2 7",
        "7 8",
        "6 8",
        "6 7",
        "8 5",
    ]


def C240():
    "C240 fullerene (https://en.wikipedia.org/wiki/Fullerene)"
    return [
        "201 1",
        "1 2",
        "1 5",
        "206 2",
        "2 3",
        "3 215",
        "3 4",
        "5 4",
        "4 211",
        "5 207",
        "235 6",
        "6 7",
        "6 10",
        "7 203",
        "7 8",
        "8 9",
        "8 202",
        "10 9",
        "9 210",
        "10 237",
        "15 11",
        "11 12",
        "11 231",
        "13 12",
        "12 219",
        "14 13",
        "13 205",
        "204 14",
        "15 14",
        "233 15",
        "20 16",
        "16 17",
        "16 227",
        "18 17",
        "17 217",
        "19 18",
        "216 18",
        "220 19",
        "19 20",
        "229 20",
        "22 21",
        "221 21",
        "21 25",
        "213 22",
        "23 22",
        "212 23",
        "23 24",
        "218 24",
        "24 25",
        "25 225",
        "27 26",
        "239 26",
        "26 30",
        "209 27",
        "27 28",
        "208 28",
        "28 29",
        "30 29",
        "29 214",
        "30 224",
        "32 31",
        "35 31",
        "31 195",
        "33 32",
        "191 32",
        "187 33",
        "33 34",
        "181 34",
        "34 35",
        "35 186",
        "37 36",
        "228 36",
        "36 40",
        "197 37",
        "37 38",
        "196 38",
        "38 39",
        "200 39",
        "39 40",
        "40 226",
        "232 41",
        "42 41",
        "41 45",
        "193 42",
        "42 43",
        "43 192",
        "43 44",
        "45 44",
        "44 198",
        "45 230",
        "236 46",
        "46 50",
        "46 47",
        "47 189",
        "47 48",
        "49 48",
        "48 188",
        "50 49",
        "49 194",
        "50 234",
        "55 51",
        "51 240",
        "51 52",
        "53 52",
        "52 183",
        "54 53",
        "53 182",
        "190 54",
        "54 55",
        "238 55",
        "60 56",
        "57 56",
        "56 222",
        "58 57",
        "57 199",
        "185 58",
        "59 58",
        "184 59",
        "59 60",
        "223 60",
        "66 61",
        "61 62",
        "61 184",
        "63 62",
        "62 185",
        "64 63",
        "63 186",
        "181 64",
        "65 64",
        "182 65",
        "65 66",
        "183 66",
        "72 67",
        "190 67",
        "67 68",
        "68 69",
        "68 182",
        "70 69",
        "69 181",
        "71 70",
        "70 187",
        "72 71",
        "188 71",
        "189 72",
        "194 73",
        "73 74",
        "73 78",
        "188 74",
        "74 75",
        "75 187",
        "75 76",
        "77 76",
        "76 191",
        "78 77",
        "77 192",
        "193 78",
        "80 79",
        "198 79",
        "79 84",
        "192 80",
        "80 81",
        "191 81",
        "81 82",
        "82 195",
        "82 83",
        "84 83",
        "83 196",
        "84 197",
        "86 85",
        "90 85",
        "85 200",
        "87 86",
        "196 86",
        "195 87",
        "88 87",
        "186 88",
        "88 89",
        "185 89",
        "89 90",
        "90 199",
        "204 91",
        "96 91",
        "91 92",
        "92 205",
        "92 93",
        "94 93",
        "93 206",
        "95 94",
        "94 201",
        "96 95",
        "95 202",
        "203 96",
        "210 97",
        "98 97",
        "97 102",
        "202 98",
        "98 99",
        "201 99",
        "99 100",
        "100 101",
        "100 207",
        "102 101",
        "101 208",
        "102 209",
        "104 103",
        "103 214",
        "103 108",
        "208 104",
        "105 104",
        "207 105",
        "105 106",
        "211 106",
        "106 107",
        "107 108",
        "107 212",
        "108 213",
        "114 109",
        "110 109",
        "109 218",
        "111 110",
        "110 212",
        "211 111",
        "112 111",
        "215 112",
        "112 113",
        "216 113",
        "113 114",
        "114 217",
        "120 115",
        "115 220",
        "115 116",
        "117 116",
        "116 216",
        "118 117",
        "117 215",
        "119 118",
        "206 118",
        "205 119",
        "119 120",
        "219 120",
        "122 121",
        "121 126",
        "121 222",
        "123 122",
        "223 122",
        "224 123",
        "123 124",
        "214 124",
        "124 125",
        "213 125",
        "125 126",
        "126 221",
        "199 127",
        "127 128",
        "127 132",
        "222 128",
        "128 129",
        "221 129",
        "129 130",
        "225 130",
        "131 130",
        "132 131",
        "226 131",
        "200 132",
        "138 133",
        "228 133",
        "133 134",
        "134 135",
        "134 226",
        "136 135",
        "135 225",
        "137 136",
        "218 136",
        "217 137",
        "138 137",
        "227 138",
        "144 139",
        "139 197",
        "139 140",
        "141 140",
        "140 228",
        "142 141",
        "141 227",
        "229 142",
        "143 142",
        "230 143",
        "143 144",
        "198 144",
        "150 145",
        "232 145",
        "145 146",
        "146 147",
        "146 230",
        "148 147",
        "147 229",
        "149 148",
        "148 220",
        "219 149",
        "150 149",
        "231 150",
        "156 151",
        "151 152",
        "151 193",
        "153 152",
        "152 232",
        "154 153",
        "153 231",
        "233 154",
        "155 154",
        "234 155",
        "155 156",
        "156 194",
        "157 162",
        "157 236",
        "157 158",
        "158 159",
        "158 234",
        "159 160",
        "159 233",
        "161 160",
        "160 204",
        "162 161",
        "161 203",
        "162 235",
        "164 163",
        "163 189",
        "163 168",
        "236 164",
        "164 165",
        "235 165",
        "165 166",
        "166 237",
        "166 167",
        "168 167",
        "167 238",
        "168 190",
        "170 169",
        "169 174",
        "169 240",
        "171 170",
        "238 170",
        "237 171",
        "171 172",
        "210 172",
        "172 173",
        "173 174",
        "173 209",
        "174 239",
        "180 175",
        "176 175",
        "175 223",
        "177 176",
        "176 184",
        "178 177",
        "183 177",
        "240 178",
        "178 179",
        "239 179",
        "179 180",
        "180 224",
    ]


def Petersen_graph():
    "https://en.wikipedia.org/wiki/Petersen_graph"
    return [
        "1 2",
        "1 3",
        "3 4",
        "4 5",
        "5 2",
        "4 6",
        "2 7",
        "1 8",
        "5 9",
        "3 10",
        "10 7",
        "7 6",
        "6 8",
        "8 9",
        "9 10",
    ]


@pytest.mark.parametrize(
    ("graph", "expected_labeling"),
    [
        (Carhart_Fig1, {1: 8, 2: 6, 6: 5, 8: 7, 3: 1, 4: 9, 10: 0, 5: 2, 9: 4, 7: 3}),
        (
            Carhart_Fig2,
            {
                1: 7,
                2: 5,
                6: 1,
                8: 9,
                3: 10,
                7: 11,
                4: 3,
                5: 4,
                9: 0,
                10: 8,
                11: 6,
                12: 2,
            },
        ),
        (
            Carhart_Fig4,
            {
                1: 3,
                2: 14,
                6: 8,
                3: 6,
                4: 1,
                8: 12,
                5: 2,
                7: 7,
                9: 11,
                10: 10,
                13: 9,
                14: 5,
                11: 15,
                12: 4,
                15: 13,
                16: 0,
            },
        ),
        (
            Schneider_Fig4c,
            {
                1: 4,
                2: 9,
                3: 10,
                4: 13,
                5: 14,
                6: 5,
                7: 0,
                8: 6,
                9: 12,
                10: 15,
                11: 1,
                12: 11,
                13: 7,
                14: 8,
                15: 3,
                16: 2,
            },
        ),
        (
            Krotko_Fig1,
            {
                1: 4,
                2: 6,
                3: 12,
                4: 10,
                5: 13,
                6: 7,
                7: 0,
                8: 1,
                9: 14,
                10: 15,
                11: 8,
                12: 5,
                13: 11,
                14: 9,
                15: 2,
                16: 3,
            },
        ),
        (Krotko_Fig2, {1: 3, 2: 7, 3: 5, 4: 4, 5: 2, 6: 6, 7: 0, 8: 1}),
        (
            C240,
            {
                201: 58,
                1: 45,
                2: 28,
                5: 54,
                206: 18,
                3: 25,
                215: 13,
                4: 44,
                211: 51,
                207: 78,
                235: 125,
                6: 117,
                7: 93,
                10: 131,
                203: 77,
                8: 97,
                9: 121,
                202: 82,
                210: 135,
                237: 158,
                15: 37,
                11: 32,
                12: 14,
                231: 34,
                13: 19,
                219: 7,
                14: 35,
                205: 12,
                204: 48,
                233: 63,
                20: 16,
                16: 24,
                17: 21,
                227: 42,
                18: 10,
                217: 33,
                19: 8,
                216: 6,
                220: 2,
                229: 23,
                22: 100,
                21: 109,
                221: 138,
                25: 99,
                213: 112,
                23: 73,
                212: 64,
                24: 72,
                218: 62,
                225: 104,
                27: 163,
                26: 178,
                239: 194,
                30: 173,
                209: 154,
                28: 145,
                208: 124,
                29: 150,
                214: 141,
                224: 184,
                32: 182,
                31: 187,
                35: 206,
                195: 177,
                33: 197,
                191: 164,
                187: 191,
                34: 210,
                181: 220,
                186: 215,
                37: 110,
                36: 105,
                228: 84,
                40: 123,
                197: 101,
                38: 136,
                196: 148,
                39: 142,
                200: 162,
                226: 115,
                232: 47,
                41: 59,
                42: 81,
                45: 56,
                193: 95,
                43: 91,
                192: 118,
                44: 79,
                198: 87,
                230: 43,
                236: 137,
                46: 143,
                50: 127,
                47: 161,
                189: 180,
                48: 155,
                49: 132,
                188: 167,
                194: 122,
                234: 103,
                55: 213,
                51: 225,
                240: 218,
                52: 234,
                53: 228,
                183: 237,
                54: 216,
                182: 233,
                190: 207,
                238: 198,
                60: 212,
                56: 199,
                57: 202,
                222: 181,
                58: 219,
                199: 192,
                185: 222,
                59: 224,
                184: 232,
                223: 205,
                66: 238,
                61: 235,
                62: 231,
                63: 227,
                64: 229,
                65: 236,
                72: 195,
                67: 211,
                68: 223,
                69: 217,
                70: 200,
                71: 190,
                73: 134,
                74: 159,
                78: 120,
                75: 169,
                76: 157,
                77: 130,
                80: 126,
                79: 108,
                84: 113,
                81: 147,
                82: 153,
                83: 139,
                86: 172,
                85: 179,
                90: 196,
                87: 185,
                88: 204,
                89: 209,
                91: 41,
                96: 57,
                92: 26,
                93: 29,
                94: 46,
                95: 61,
                97: 119,
                98: 94,
                102: 129,
                99: 80,
                100: 90,
                101: 116,
                104: 107,
                103: 114,
                108: 102,
                105: 86,
                106: 70,
                107: 75,
                114: 31,
                109: 38,
                110: 39,
                111: 36,
                112: 20,
                113: 15,
                120: 0,
                115: 239,
                116: 1,
                117: 4,
                118: 5,
                119: 3,
                122: 186,
                121: 175,
                126: 149,
                123: 176,
                124: 152,
                125: 140,
                127: 171,
                128: 166,
                132: 156,
                129: 144,
                130: 128,
                131: 133,
                138: 55,
                133: 76,
                134: 92,
                135: 88,
                136: 65,
                137: 52,
                144: 69,
                139: 74,
                140: 68,
                141: 49,
                142: 40,
                143: 50,
                150: 22,
                145: 30,
                146: 27,
                147: 17,
                148: 9,
                149: 11,
                156: 96,
                151: 83,
                152: 60,
                153: 53,
                154: 66,
                155: 89,
                157: 111,
                162: 106,
                158: 98,
                159: 71,
                160: 67,
                161: 85,
                164: 151,
                163: 174,
                168: 188,
                165: 146,
                166: 165,
                167: 183,
                170: 193,
                169: 201,
                174: 189,
                171: 170,
                172: 160,
                173: 168,
                180: 203,
                175: 214,
                176: 226,
                177: 230,
                178: 221,
                179: 208,
            },
        ),
        (Petersen_graph, {1: 7, 2: 5, 3: 6, 4: 8, 5: 2, 6: 3, 7: 9, 8: 4, 9: 1, 10: 0}),
    ],
    ids=lambda param: getattr(param, "__name__", None),
)
def test_regression(graph, expected_labeling):
    G = nx.parse_edgelist(graph(), nodetype=int)
    labeling = iso.canonical_labeling(G)

    assert labeling == expected_labeling


def permute_graph(
    G: nx.Graph,
) -> nx.Graph:
    """Randomly permute G's node labels."""
    random.seed(
        42
    )  # Subsequent calls of random.shuffle(x[, random]) will now use fixed sequence of values for `random` parameter.

    G_permuted = _permute_graph(G)

    while nx.utils.graphs_equal(G, G_permuted):
        G_permuted = _permute_graph(G)

    return G_permuted


def _permute_graph(G: nx.Graph) -> nx.Graph:
    labels = list(G.nodes)
    permuted_labels = list(labels)  # shallow copy
    random.shuffle(permuted_labels)
    G_relabeled = nx.relabel_nodes(
        G, dict(zip(permuted_labels, labels, strict=True)), copy=True
    )

    return _sort_graph_by_label(G_relabeled)


def _sort_graph_by_label(G: nx.Graph) -> nx.Graph:
    """Sort graph by label.

    Ensure that the graph's node iteration order is identical to the label order.
    In a NetworkX graph, the iteration order of the nodes depends on the initial
    insertion order of the nodes. There's a crucial difference to `nx.relabel_nodes()`.
    The latter only changes the labels, without changing the iteration order.

    Original nodes:
        label | attribute
        -----------------
        0     | A
        1     | B
        2     | C

    Nodes relabeled with `nx.relabel_nodes()`:
        label | attribute
        -----------------
        1     | A
        2     | B
        0     | C

    In contrast, the present function changes the labels _and_ iteration order:
        label | attribute
        -----------------
        0     | C
        1     | A
        2     | B
    """
    nodes_sorted_by_label = sorted(G.nodes(data=True))

    G_sorted_by_label = nx.Graph()
    G_sorted_by_label.add_nodes_from(nodes_sorted_by_label)
    G_sorted_by_label.add_edges_from(G.edges(data=True))

    return G_sorted_by_label


@pytest.mark.parametrize(
    "graph",
    [
        Carhart_Fig1,
        Carhart_Fig2,
        Carhart_Fig4,
        Schneider_Fig4c,
        Krotko_Fig1,
        Krotko_Fig2,
        C240,
        Petersen_graph,
    ],
    ids=lambda param: getattr(param, "__name__", None),
)
def test_invariance(graph):
    G = nx.parse_edgelist(graph(), nodetype=int)
    G_permuted = permute_graph(G)

    assert not nx.utils.graphs_equal(G, G_permuted)

    labeling = iso.canonical_labeling(G)
    permuted_labeling = iso.canonical_labeling(G_permuted)

    G_canonical = nx.relabel_nodes(G, labeling)
    G_permuted_canonical = nx.relabel_nodes(G_permuted, permuted_labeling)

    assert nx.utils.graphs_equal(G_canonical, G_permuted_canonical)


def _refinement_tree_depth(G, node_attributes=()):
    canon = iso.canonicalization
    invariant_values = {
        node: tuple(attributes[attribute] for attribute in node_attributes)
        for node, attributes in G.nodes(data=True)
    }
    neighbors = {node: tuple(G[node]) for node in G}
    partitions, _ = canon.get_partitions_from_attributes(invariant_values, neighbors)
    edges = list(G.edges())

    return len(list(canon.get_refinement_tree_levels(partitions, neighbors, edges)))


def _c240_with_attributes():
    # Each attribute is set to a distinct value on a single, different node.
    G = nx.parse_edgelist(C240(), nodetype=int)
    nx.set_node_attributes(G, 0, "foo")
    nx.set_node_attributes(G, 0, "bar")
    G.nodes[next(iter(G))]["foo"] = 42
    G.nodes[83]["bar"] = 42

    return G


def test_canonical_labeling_raises_on_missing_node_attribute():
    G = nx.path_graph(2)
    G.nodes[0]["foo"] = 1

    with pytest.raises(KeyError, match="Node 1 is missing attributes: foo"):
        iso.canonical_labeling(G, ["foo"])


def test_c240_node_attributes_reduce_refinement_tree_levels():
    G = _c240_with_attributes()

    levels = [
        _refinement_tree_depth(G, attrs) for attrs in ([], ["foo"], ["foo", "bar"])
    ]

    assert levels[0] > levels[1] > levels[2]


def test_c240_node_attributes_reduce_canonical_labeling_runtime():
    G = _c240_with_attributes()

    def timed(attrs):
        start = time.perf_counter()
        iso.canonical_labeling(G, attrs)
        return time.perf_counter() - start

    t0, t1, t2 = (
        min(timed(attrs) for _ in range(2)) for attrs in ([], ["foo"], ["foo", "bar"])
    )

    assert t0 > t1 > t2
