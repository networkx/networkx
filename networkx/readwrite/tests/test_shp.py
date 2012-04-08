"""Unit tests for shp.
"""

import os,tempfile
from nose import SkipTest
from nose.tools import assert_equal

import networkx as nx

class TestShp(object):
    @classmethod
    def setupClass(cls):
        global ogr
        try:
            from osgeo import ogr
        except ImportError:
            raise SkipTest('ogr not available.')

    def deletetmp(self, drv, *paths):
        for p in paths:
            if os.path.exists(p): drv.DeleteDataSource(p)

    def setUp(self):

        def createlayer(driver):
            lyr = shp.CreateLayer("edges", None, ogr.wkbLineString)
            namedef = ogr.FieldDefn("Name", ogr.OFTString)
            namedef.SetWidth(32)
            lyr.CreateField(namedef)
            return lyr

        drv = ogr.GetDriverByName("ESRI Shapefile")

        testdir = os.path.join(tempfile.gettempdir(),'shpdir')
        shppath = os.path.join(tempfile.gettempdir(),'tmpshp.shp')

        self.deletetmp(drv, testdir, shppath)
        os.mkdir(testdir)

        shp = drv.CreateDataSource(shppath)
        lyr = createlayer(shp)
        self.names = ['a','b','c']  #edgenames
        self.paths = (  [(1.0, 1.0), (2.0, 2.0)],
                        [(2.0, 2.0), (3.0, 3.0)],
                        [(0.9, 0.9), (4.0, 2.0)]
                    )
        for path,name in zip(self.paths, self.names):
            feat = ogr.Feature(lyr.GetLayerDefn())
            g = ogr.Geometry(ogr.wkbLineString)
            map(lambda xy: g.AddPoint_2D(*xy), path)
            feat.SetGeometry(g)
            feat.SetField("Name", name)
            lyr.CreateFeature(feat)
        self.shppath = shppath
        self.testdir = testdir
        self.drv = drv

    def testload(self):
        expected = nx.DiGraph()
        map(expected.add_path, self.paths)
        G = nx.read_shp(self.shppath)
        assert_equal(sorted(expected.node), sorted(G.node))
        assert_equal(sorted(expected.edges()), sorted(G.edges()))
        names = [G.get_edge_data(s,e)['Name'] for s,e in G.edges()]
        assert_equal(self.names, sorted(names))

    def checkgeom(self, lyr, expected):
        feature = lyr.GetNextFeature()
        actualwkt = []
        while feature:
            actualwkt.append(feature.GetGeometryRef().ExportToWkt())
            feature = lyr.GetNextFeature()
        assert_equal(sorted(expected), sorted(actualwkt))

    def test_geometryexport(self):
        expectedpoints = (
            "POINT (1 1)",
            "POINT (2 2)",
            "POINT (3 3)",
            "POINT (0.9 0.9)",
            "POINT (4 2)"
        )
        expectedlines = (
            "LINESTRING (1 1,2 2)",
            "LINESTRING (2 2,3 3)",
            "LINESTRING (0.9 0.9,4 2)"
        )
        tpath = os.path.join(tempfile.gettempdir(),'shpdir')
        G = nx.read_shp(self.shppath)
        nx.write_shp(G, tpath)
        shpdir = ogr.Open(tpath)
        self.checkgeom(shpdir.GetLayerByName("nodes"), expectedpoints)
        self.checkgeom(shpdir.GetLayerByName("edges"), expectedlines)

    def test_attributeexport(self):
        def testattributes(lyr, expected):
            feature = lyr.GetNextFeature()
            actualvalues = []
            while feature:
                actualvalues.append(feature.GetGeometryRef().ExportToWkt())
                feature = lyr.GetNextFeature()
            assert_equal(sorted(expected), sorted(actualvalues))

        tpath = os.path.join(tempfile.gettempdir(),'shpdir')
        G = nx.read_shp(self.shppath)
        nx.write_shp(G, tpath)
        shpdir = ogr.Open(tpath)
        nodes = shpdir.GetLayerByName("nodes")

    def test_wkt_export(self):
        G = nx.DiGraph()
        tpath = os.path.join(tempfile.gettempdir(),'shpdir')
        points = (
            "POINT (0.9 0.9)",
            "POINT (4 2)"
        )
        line = (
            "LINESTRING (0.9 0.9,4 2)",
        )
        G.add_node(1, Wkt=points[0])
        G.add_node(2, Wkt=points[1])
        G.add_edge(1, 2, Wkt=line[0])
        try:
            nx.write_shp(G, tpath)
        except Exception as e:
            assert False, e
        shpdir = ogr.Open(tpath)
        self.checkgeom(shpdir.GetLayerByName("nodes"), points)
        self.checkgeom(shpdir.GetLayerByName("edges"), line)

    def tearDown(self):
        self.deletetmp(self.drv, self.testdir, self.shppath)
