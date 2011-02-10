"""
Unit tests for shp.
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
            
    def setUp(self):
        drv = ogr.GetDriverByName("ESRI Shapefile")
        shppath = os.path.join(tempfile.gettempdir(),'tmpshp.shp')
        if os.path.exists(shppath): 
            drv.DeleteDataSource(shppath)      
        shp = drv.CreateDataSource(shppath)
        lyr = shp.CreateLayer( "edges", None, ogr.wkbLineString)
        
        self.paths = (  [(7.0, 1.0), (1.0, 1.0)],
                        [(2.0, 2.0), (3.0, 3.0)],
                        [(4.0, 1.0), (2.0, 2.0)]
                    )
        for path in self.paths:
            feat = ogr.Feature(lyr.GetLayerDefn())
            g = ogr.Geometry(ogr.wkbLineString)
            for xy in path:
                g.AddPoint_2D(*xy)
            feat.SetGeometry(g)
            lyr.CreateFeature(feat)
        self.shppath = shppath
        self.drv = drv
        
    def testload(self):
        expected = nx.DiGraph()
        for p in self.paths:
            expected.add_path(p)
        actual = nx.read_shp(self.shppath)
        assert_equal(sorted(expected.node), sorted(actual.node))
        assert_equal(sorted(expected.edges()), sorted(actual.edges()))
    
    def tearDown(self):
        self.drv.DeleteDataSource(self.shppath)
