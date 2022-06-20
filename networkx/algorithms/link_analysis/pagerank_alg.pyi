from typing import Optional

def pagerank(
    G,
    alpha: float = ...,
    personalization: Optional[dict] = ...,
    max_iter: int = ...,
    tol: float = ...,
    nstart: Optional[dict] = ...,
    weight: str = ...,
    dangling: Optional[dict] = ...,
): ...
def google_matrix(
    G,
    alpha: float = ...,
    personalization: Optional[dict] = ...,
    nodelist: Optional[list] = ...,
    weight: str = ...,
    dangling: Optional[dict] = ...,
): ...
def pagerank_numpy(
    G,
    alpha: float = ...,
    personalization: Optional[dict] = ...,
    weight: str = ...,
    dangling: Optional[dict] = ...,
): ...
def pagerank_scipy(
    G,
    alpha: float = ...,
    personalization: Optional[dict] = ...,
    max_iter: int = ...,
    tol: float = ...,
    nstart: Optional[dict] = ...,
    weight: str = ...,
    dangling: Optional[dict] = ...,
): ...
