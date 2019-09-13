#    Copyright (C) 2019 by
#    Luca Cappelletti
#    MIT license.
#
# Authors:
#    Luca Cappelletti <cappelletti.luca@studenti.unimi.it>
#
"""Functions for computing the harmonic centrality of a graph using multiprocessing and caching."""
from multiprocessing import Pool, cpu_count
from math import ceil
import os
import shutil
from collections import ChainMap
from .harmonic import harmonic_centrality

__all__ = ['parallel_harmonic_centrality']


def _build_path(nodes, cache_dir):
    """Return path corresponding to given nodes.
        nodes: container
            Container of nodes, used to determine the unique
            hash to build the cache path.
        cache_dir: string
            Directory where to store the partial results.
    """
    from dict_hash import sha256
    return "{cache_dir}/{hashcode}.json.gz".format(
        cache_dir=cache_dir,
        hashcode=sha256(nodes)
    )


def _build_tmp_path(path):
    """Return, given a path, its default placeholder path.

    This is necessary for when the code is run on computing SLURM clusters,
    where multiple parallel nodes work on the same virtual disk.
    With this simple tweak parallelization can be achieved without having to
    use tools such as OpenMPI at this scale, accepting a non-zero collision risk.
    """
    return "{path}.tmp".format(path=path)


def _clear_cache(cache_dir):
    """Delete given cache dir.
        cache_dir: string
            Directory where to store the partial results.
    """
    shutil.rmtree(cache_dir)


def _job(G, nbunch, distance, cache, cache_dir):
    import compress_json
    from touch import touch
    try:
        if cache:
            path = _build_path(nbunch, cache_dir)
            if os.path.exists(path):
                return compress_json.load(path)
            tmp_path = _build_tmp_path(path)
            if os.path.exists(tmp_path):
                return {}
            os.makedirs(os.path.dirname(path), exist_ok=True)
            touch(tmp_path)
        
        result = harmonic_centrality(G, nbunch=nbunch, distance=distance)

        if cache:
            compress_json.dump(result, path)
            os.remove(tmp_path)

        return result
    except (Exception, KeyboardInterrupt) as e:
        if cache and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise e
    

def _job_wrapper(task):
    return _job(*task)

def _tasks(G, nbunch, distance, cache, cache_dir, n):
    """Yield successive n equally sized nbunch from graphs with task arguments."""
    return (
        (G, nbunch[i:i + n], distance, cache, cache_dir)
        for i in range(0, len(nbunch), n)
    )

def parallel_harmonic_centrality(G, n=100, nbunch=None, distance=None, verbose=False, cache=False, cache_dir=".parallel_harmonic_centrality"):
    r"""Compute harmonic centrality for nodes.
    """
    from auto_tqdm import tqdm
    nbunch = list(G.nodes) if nbunch is None else nbunch
    total = ceil(len(nbunch)/n)
    if total==0:
        return {}
    with Pool(min(cpu_count(), total)) as p:
        results = dict(ChainMap(*list(tqdm(
            p.imap(_job_wrapper, _tasks(G, nbunch, distance, cache, cache_dir, n)),
            total=total,
            verbose=verbose
        ))))
    if cache:
        _clear_cache(cache_dir)
    return results


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        from auto_tqdm import tqdm
        from dict_hash import sha256
        import compress_json
        from touch import touch
    except:
        raise SkipTest("SciPy not available")
