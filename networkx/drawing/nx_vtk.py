"""
Draw networks in 3d with vtk.

References:
 - vtk:     http://www.vtk.org/

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import vtk
from vtk.util.colors import banana, plum
import networkx

# this is a hack for drawing a network in 3d with vtk
# perhaps it will inspire someone to submit a polished version?
# much of the code borrowed from the vtk examples

def draw_nxvtk(G, node_pos):
    """
    Draw networkx graph in 3d with nodes at node_pos.

    See layout.py for functions that compute node positions.

    node_pos is a dictionary keyed by vertex with a three-tuple
    of x-y positions as the value.

    The node color is plum.
    The edge color is banana.

    All the nodes are the same size.

    """
    # set node positions
    np={}
    for n in G.nodes():
        try:
            np[n]=node_pos[n]
        except KeyError:
            raise networkx.NetworkXError, "node %s doesn't have position"%n

    nodePoints = vtk.vtkPoints()

    i=0
    for (x,y,z) in np.values():
        nodePoints.InsertPoint(i, x, y, z)
        i=i+1

    # Create a polydata to be glyphed.
    inputData = vtk.vtkPolyData()
    inputData.SetPoints(nodePoints)

    # Use sphere as glyph source.
    balls = vtk.vtkSphereSource()
    balls.SetRadius(.05)
    balls.SetPhiResolution(20)
    balls.SetThetaResolution(20)

    glyphPoints = vtk.vtkGlyph3D()
    glyphPoints.SetInput(inputData)
    glyphPoints.SetSource(balls.GetOutput())

    glyphMapper = vtk.vtkPolyDataMapper()
    glyphMapper.SetInput(glyphPoints.GetOutput())

    glyph = vtk.vtkActor()
    glyph.SetMapper(glyphMapper)
    glyph.GetProperty().SetDiffuseColor(plum)
    glyph.GetProperty().SetSpecular(.3)
    glyph.GetProperty().SetSpecularPower(30)

    # Generate the polyline for the spline.
    points = vtk.vtkPoints()
    edgeData = vtk.vtkPolyData()

    # Edges

    lines = vtk.vtkCellArray()
    i=0
    for e in G.edges_iter():
        # The edge e can be a 2-tuple (Graph) or a 3-tuple (Xgraph)
        u=e[0]
        v=e[1]
        if v in node_pos and u in node_pos:
            lines.InsertNextCell(2)
            for n in (u,v):
                (x,y,z)=node_pos[n]
                points.InsertPoint(i, x, y, z)
                lines.InsertCellPoint(i)
                i=i+1

    edgeData.SetPoints(points)
    edgeData.SetLines(lines)

    # Add thickness to the resulting line.
    Tubes = vtk.vtkTubeFilter()
    Tubes.SetNumberOfSides(16)
    Tubes.SetInput(edgeData)
    Tubes.SetRadius(.01)
    #
    profileMapper = vtk.vtkPolyDataMapper()
    profileMapper.SetInput(Tubes.GetOutput())

    # 
    profile = vtk.vtkActor()
    profile.SetMapper(profileMapper)
    profile.GetProperty().SetDiffuseColor(banana)
    profile.GetProperty().SetSpecular(.3)
    profile.GetProperty().SetSpecularPower(30)

    # Now create the RenderWindow, Renderer and Interactor
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Add the actors
    ren.AddActor(glyph)
    ren.AddActor(profile)

    renWin.SetSize(640, 640)

    iren.Initialize()
    renWin.Render()
    iren.Start()
