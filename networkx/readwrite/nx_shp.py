"""
*********
Shapefile
*********

Generates a networkx.DiGraph from point and line shapefiles.

Point geometries are translated into nodes, lines into edges. Coordinate tuples
are used as keys. Attributes are preserved, line geometries are simplified into
start and end coordinates. Accepts a single shapefile or directory of many
shapefiles.

"The Esri Shapefile or simply a shapefile is a popular geospatial vector
data format for geographic information systems software. It is developed
and regulated by Esri as a (mostly) open specification for data
interoperability among Esri and other software products."
See http://en.wikipedia.org/wiki/Shapefile for additional information.

"""
__author__ = """Ben Reilly (benwreilly@gmail.com)"""
#    Copyright (C) 2004-2010 by
#    Ben Reilly <benwreilly@gmail.com>
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['read_shp']

import networkx as nx

def read_shp(path):
    """Generate a directed graph from shapefiles.

    "The Esri Shapefile or simply a shapefile is a popular geospatial vector
    data format for geographic information systems software [1]_."

    Point geometries are translated into nodes, lines into
    edges. Coordinate tuples are used as keys. Attributes are preserved,
    line geometries are simplified into start and end coordinates.

    Parameters
    ----------
    path : string 
      File name or directory name.

    Returns
    -------
    G : NetworkX DiGraph

    Examples
    --------
    G=nx.read_shp('test.shp')
    
    Notes
    -----
    Uses Python bindings for OGR in the GDAL library, http://www.gdal.org.
    Available for Linux in the python-gdal package.

    References
    ----------
    .. [1] http://en.wikipedia.org/wiki/Shapefile
    """
    try:
        from osgeo import ogr
    except ImportError:
        raise ImportError("read_shp() requires OGR: http://www.gdal.org/")
    
    def getfieldinfo(lyr, feature, flds):
            f = feature
            return [f.GetField(f.GetFieldIndex(x)) for x in flds]
            
    def addlyr(G,lyr, fields):
        for findex in xrange(lyr.GetFeatureCount()):
            f = lyr.GetFeature(findex)
            flddata = getfieldinfo(lyr, f, fields)
            g = f.geometry()
            attributes = dict(zip(fields, flddata))
            attributes["ShpName"] = lyr.GetName()
            if g.GetGeometryType() == 1: #point
                G.add_node((g.GetPoint_2D(0)), attributes)
            if g.GetGeometryType() == 2: #linestring
                last = g.GetPointCount() - 1
                G.add_edge(g.GetPoint_2D(0), g.GetPoint_2D(last), attributes)
        return G
                
    G = nx.DiGraph()
    shp = ogr.Open(path)
    lyrcount = shp.GetLayerCount() # multiple layers indicate a directory 
    for lyrindex in xrange(lyrcount):
        lyr = shp.GetLayerByIndex(lyrindex)
        flds = [x.GetName() for x in lyr.schema]
        G=addlyr(G, lyr, flds)
    
    return G
    
# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import ogr
    except:
        raise SkipTest("OGR not available")
