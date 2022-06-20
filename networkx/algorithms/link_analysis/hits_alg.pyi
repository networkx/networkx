from typing import Optional

def hits(
    G,
    max_iter: int = ...,
    tol: float = ...,
    nstart: Optional[dict] = ...,
    normalized: bool = ...,
): ...
def authority_matrix(G, nodelist: Optional[dict] = ...): ...
def hub_matrix(G, nodelist: Optional[dict] = ...): ...
def hits_numpy(G, normalized: bool = ...): ...
def hits_scipy(
    G,
    max_iter: int = ...,
    tol: float = ...,
    nstart: Optional[dict] = ...,
    normalized: bool = ...,
): ...
