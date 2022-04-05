def generate_adjacency_tensor(
    G: nx.Graph, funcs: List[Callable], return_array=False
) -> xr.DataArray:
    mats = []
    for func in funcs:
        mats.append(func(G))
    da = xr.concat(mats, dim="name")
    if return_array:
        return da.data
    return da
