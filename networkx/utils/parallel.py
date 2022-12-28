import itertools
import importlib
from typing import Callable, Iterable, Any, Optional

try:
    import joblib
except ImportError:
    raise ImportError(
        "joblib is not installed. Install joblib using 'pip install joblib'."
    )

SUPPORTED_BACKENDS = [
    "multiprocessing",
    "dask",
    "ray",
    "loky",
    "threading",
    "ipyparallel",
]


def optional_package(pkg_name):
    """Import an optional package and return the package and whether it was found.

    Parameters
    ----------
    pkg_name : str
        The name of the package to import.

    Returns
    -------
    pkg : module
        The imported package.
    has_pkg : bool
        Whether the package was found.
    pkg_version : str
        The version of the package.

    """
    try:
        pkg = importlib.import_module(pkg_name)
        has_pkg = True
        pkg_version = pkg.__version__
    except ImportError:
        pkg = None
        has_pkg = False
        pkg_version = None
    return pkg, has_pkg, pkg_version


def chunks(l, n):
    """Divide a list `l` of nodes or edges into `n` chunks"""
    l_c = iter(l)
    while 1:
        x = tuple(itertools.islice(l_c, n))
        if not x:
            return
        yield x


class NxParallel:
    """A class to instantiate a callable object for handling parallelization of functions in NetworkX. The class is initialized by specifying a backend and the
    number of processes to use, and can then be called with a function object and an
    associated iterable as input. The function will be called on each element of the
    iterable in parallel. The class can be used with the multiprocessing, ipyparallel,
    dask, ray, and other native joblib backends.

    Attributes
    ----------
    backend : str
        The backend to use. Choose from 'multiprocessing', 'dask', 'ray', 'loky', 'threading', or 'ipyparallel'.
    processes : int
        The number of processes to use. If None, the number of processes will be set to the number
        of CPUs on the machine.

    Raises
    ------
    `ImportError`
        If joblib, or any of the optional backends are not installed.
    `ValueError`
        If an invalid backend is specified, or if the number of elements in the provided
        iterable is not equal to the number of parameters in the provided function.

    """

    def __init__(
        self,
        backend: str = "multiprocessing",
        processes: Optional[int] = None,
        **kwargs,
    ):
        self.backend = backend
        if processes is None:
            from os import cpu_count

            self.processes = cpu_count()
        else:
            self.processes = processes

        if self.backend in SUPPORTED_BACKENDS:
            # Business logic restricted to this block
            if self.backend == "dask":
                dask, has_dask, _ = optional_package("dask")
                distributed, has_distributed, _ = optional_package("distributed")
                if not has_dask or not has_distributed:
                    raise ImportError(
                        "dask[distributed] is not installed. Install dask using 'pip install dask distributed'."
                    )
                client = distributed.Client(**kwargs)
                joblib.register_parallel_backend(
                    "dask", lambda: joblib._dask.DaskDistributedBackend(client=client)
                )
            elif self.backend == "ray":
                ray, has_ray, _ = optional_package("ray")
                if not has_ray:
                    raise ImportError(
                        "ray is not installed. Install ray using 'pip install ray'."
                    )
                rb = ray.util.joblib.ray_backend.RayBackend(**kwargs)
                joblib.register_parallel_backend("ray", lambda: rb)
            elif self.backend == "ipyparallel":
                ipyparallel, has_ipyparallel, _ = optional_package("ipyparallel")
                if not has_ipyparallel:
                    raise ImportError(
                        "ipyparallel is not installed. Install ipyparallel using 'pip "
                        "install ipyparallel'."
                    )
                bview = ipyparallel.Client(**kwargs).load_balanced_view()
                joblib.register_parallel_backend(
                    "ipyparallel",
                    lambda: ipyparallel.joblib.IPythonParallelBackend(view=bview),
                )
        else:
            raise ValueError(
                f"Invalid backend specified. Choose from {SUPPORTED_BACKENDS}."
            )

    def __call__(self, func: Callable, iterable: Iterable[Any], **kwargs):
        """Call the class instance with a function and an iterable.
        The function will be called on each element of the iterable in parallel."""
        import inspect

        params = list(inspect.signature(func).parameters.keys())

        # Check that the number of elements in the iterable is equal to the number of
        # parameters in the function.
        if func.__code__.co_argcount != len(iterable):
            raise ValueError(
                "The number of elements in the iterable must be equal to the number of "
                " parameters in the function."
            )

        with joblib.parallel_backend(self.backend):
            return joblib.Parallel(n_jobs=self.processes, **kwargs)(
                joblib.delayed(func)(**dict(zip(params, i))) for i in iterable
            )
