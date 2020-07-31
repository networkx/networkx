import pytest

gpd = pytest.importorskip("geopandas")

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
    graph_from_shp = nx.from_geopandas_edgelist(
        gdf, create_using=nx.Graph, edge_attr=gdf.columns.to_list()
    )
    failed = False
    for u, v, d in graph_from_shp.edges(data=True):
        if set(d.keys()) != {"id", "attr_text", "attr_float", "geometry", "attr_int"}:
            failed = True
            break
    assert not failed


def test_from_geopandas_edgelist_directed_with_attrs():

    gdf = gpd.GeoDataFrame.from_file("geospatial_data/shp/test_shp.shp")
    graph_from_shp = nx.from_geopandas_edgelist(
        gdf, create_using=nx.DiGraph, edge_attr=gdf.columns.to_list()
    )
    failed = False
    for u, v, d in graph_from_shp.edges(data=True):
        if set(d.keys()) != {"id", "attr_text", "attr_float", "geometry", "attr_int"}:
            failed = True
            break
    assert not failed


def test_to_geopandas_edgelist():

    gdf = gpd.GeoDataFrame.from_file("geospatial_data/shp/test_shp.shp")
    graph_from_shp = nx.from_geopandas_edgelist(
        gdf, create_using=nx.DiGraph, edge_attr=gdf.columns.to_list()
    )
    new_gdf = nx.to_geopandas_edgelist(graph_from_shp, crs=3857, geometry="geometry")
    joined = gdf.join(new_gdf, rsuffix="_new")
    joined.drop(["source", "target"], axis="columns", inplace=True)
    failed = False
    for col in [c for c in joined.columns if c[-4:] != "_new"]:
        joined["test"] = joined.apply(
            lambda row: row[col] == row[f"{col}_new"], axis="columns"
        )
        # If length of set is not 1 then there is True and False
        # If The first length of set is 1 but the next iterated item is False then there is no True
        if len(set(joined["test"])) > 1 or not next(iter(set(joined["test"]))):
            failed = True
            break
    assert not failed

    print()
