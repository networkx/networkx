import geopandas as gpd
import networkx as nx


def test_from_geopandas_edgelist_undirected():

    gdf = gpd.GeoDataFrame.from_file("geospatial_data/shp/test_shp.shp")
    graph_from_shp = nx.from_geopandas_edgelist(gdf, create_using=nx.Graph)
    assert isinstance(graph_from_shp, nx.Graph)


def test_from_geopandas_edgelist_directed():

    gdf = gpd.GeoDataFrame.from_file("geospatial_data/shp/test_shp.shp")
    graph_from_shp = nx.from_geopandas_edgelist(gdf, create_using=nx.DiGraph)
    assert isinstance(graph_from_shp, nx.DiGraph)


def test_from_geopandas_edgelist_undirected_with_attrs():

    gdf = gpd.GeoDataFrame.from_file("geospatial_data/shp/test_shp.shp")
    graph_from_shp = nx.from_geopandas_edgelist(gdf, create_using=nx.Graph, edge_attr=gdf.columns.to_list())
    failed = False
    for u, v, d in graph_from_shp.edges(data=True):
        if set(d.keys()) != {'id', 'attr_text', 'attr_float', 'geometry', 'attr_int'}:
            failed = True
            break
    assert not failed


def test_from_geopandas_edgelist_directed_with_attrs():

    gdf = gpd.GeoDataFrame.from_file("geospatial_data/shp/test_shp.shp")
    graph_from_shp = nx.from_geopandas_edgelist(gdf, create_using=nx.DiGraph, edge_attr=gdf.columns.to_list())
    failed = False
    for u, v, d in graph_from_shp.edges(data=True):
        if set(d.keys()) != {'id', 'attr_text', 'attr_float', 'geometry', 'attr_int'}:
            failed = True
            break
    assert not failed
