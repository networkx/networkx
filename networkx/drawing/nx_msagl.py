"""
This is a module allowing to do layout using Microsoft Automatic Graph Layout https://github.com/microsoft/automatic-graph-layout.
It contains an impl of Sugiyama algorithm, unlike most of other other impls of Sugiyama algorythm, it is licensed under MIT License.
You need a precompiled `AutomaticGraphLayout.dll` and https://github.com/pythonnet/pythonnet.
"""

import typing
from math import pi

import clr

aglAssembly = clr.AddReference("AutomaticGraphLayout")

from Microsoft.Msagl.Core.Geometry import Point, Rectangle
from Microsoft.Msagl.Core.Geometry.Curves import Curve, CurveFactory, PlaneTransformation
from Microsoft.Msagl.Core.Layout import Edge, GeometryGraph, Node
from Microsoft.Msagl.Core.Routing import EdgeRoutingMode, EdgeRoutingSettings
from Microsoft.Msagl.Layout.Layered import LayeredLayout, SugiyamaLayoutSettings

from .. import DiGraph


def makeCurveRect(w: float = 20, h: float = 10) -> Curve:
    return CurveFactory.CreateRectangle(float(w), float(h), Point(0, 0))


def makeNode(iD: int) -> Node:
    return Node(makeCurveRect(), iD)


def graphToMsGraph(nxG: DiGraph) -> typing.Tuple[GeometryGraph, typing.Mapping[int, typing.Any], typing.Mapping[int, typing.Any]]:
    """Converts a directed graph into a `Microsoft.Msagl.Core.Layout.GeometryGraph`"""

    g = GeometryGraph()

    idToNxNodeMap = []
    revIdx = {}
    for n in nxG.nodes:
        i = len(idToNxNodeMap)
        nd = makeNode(i)
        idToNxNodeMap.append(n)
        revIdx[n] = nd
        g.Nodes.Add(nd)

    for n1, n2 in nxG.edges:
        g.Edges.Add(Edge(revIdx[n1], revIdx[n2]))

    return g, idToNxNodeMap


def sugiyama_layout(g, settings: typing.Optional[SugiyamaLayoutSettings] = None):
    if settings is None:
        settings = SugiyamaLayoutSettings()
        settings.EdgeRoutingSettings.EdgeRoutingMode = EdgeRoutingMode.Spline

    msG, idToNxNodeMap = graphToMsGraph(g)

    layout = LayeredLayout(msG, settings)
    layout.Run()

    return {idToNxNodeMap[n.UserData]: (n.Center.X, n.Center.Y) for n in list(msG.Nodes)}
