"""
Utilities to just-in-time-cythonize a module at runtime.
"""
from collections import defaultdict
from os.path import dirname, join, basename, splitext, exists
import os
import warnings


# Track the number of times we've tried to autojit specific pyx files
NUM_AUTOJIT_TRIES = defaultdict(lambda: 0)
MAX_AUTOJIT_TRIES = 1


def import_module_from_pyx(fname, dpath, error="raise", autojit=True, verbose=1):
    """
    Attempts to import a module corresponding to a pyx file.

    If the corresponding compiled module is not found, this can attempt to
    JIT-cythonize the pyx file.

    Parameters
    ----------
    fname : str
        The basename of the cython pyx file

    dpath : str
        The directory containing the cython pyx file

    error : str
        Can be "raise" or "ignore"

    autojit : bool
        If True, we will cythonize and compile the pyx file if possible.

    verbose : int
        verbosity level (higher is more verbose)

    Returns
    -------
    ModuleType | None : module
        Returns the compiled and imported module if possible, otherwise None

    Ignore
    ------
    from networkx.algorithms.string._autojit import *
    fname = "balanced_embedding_cython.pyx"
    dpath = ub.expandpath('$HOME/code/networkx/networkx/algorithms/string')
    module = import_module_from_pyx(fname, dpath, error="ignore", verbose=1)
    print('module = {!r}'.format(module))
    """
    pyx_fpath = join(dpath, fname)
    if not exists(pyx_fpath):
        raise AssertionError("pyx file {!r} does not exist".format(pyx_fpath))

    try:
        # This functionality depends on ubelt
        # TODO: the required functionality could be moved to nx.utils
        import ubelt as ub
    except Exception:
        if verbose:
            print("Autojit requires ubelt, which failed to import")
        if error == "ignore":
            module = None
        elif error == "raise":
            raise
        else:
            raise KeyError(error)
    else:

        if autojit:
            # Try to JIT the cython module if we ship the pyx without the compiled
            # library.
            NUM_AUTOJIT_TRIES[pyx_fpath] += 1
            if NUM_AUTOJIT_TRIES[pyx_fpath] <= MAX_AUTOJIT_TRIES:
                try:
                    _autojit_cython(pyx_fpath, verbose=verbose)
                except Exception as ex:
                    warnings.warn("Cython autojit failed: ex={!r}".format(ex))
                    if error == "raise":
                        raise

        try:
            module = ub.import_module_from_path(pyx_fpath)
        except Exception:
            if error == "ignore":
                module = None
            elif error == "raise":
                raise
            else:
                raise KeyError(error)

        return module


def _platform_pylib_exts():  # nocover
    """
    Returns .so, .pyd, or .dylib depending on linux, win or mac.  Returns the
    previous with and without abi (e.g. .cpython-35m-x86_64-linux-gnu) flags.
    """
    import sysconfig

    valid_exts = []
    # handle PEP 3149 -- ABI version tagged .so files
    base_ext = "." + sysconfig.get_config_var("EXT_SUFFIX").split(".")[-1]
    # ABI = application binary interface
    tags = [
        sysconfig.get_config_var("SOABI"),
        "abi3",  # not sure why this one is valid, but it is
    ]
    tags = [t for t in tags if t]
    for tag in tags:
        valid_exts.append("." + tag + base_ext)
    # return with and without API flags
    valid_exts.append(base_ext)
    valid_exts = tuple(valid_exts)
    return valid_exts


def _autojit_cython(pyx_fpath, verbose=1):
    """
    This idea is that given a pyx file, we try to compile it. We write a stamp
    file so subsequent calls should be very fast as long as the source pyx has
    not changed.

    Parameters
    ----------
    pyx_fpath : str
        path to the pyx file

    verbose : int
        higher is more verbose.
    """
    import shutil

    # TODO: move necessary ubelt utilities to nx.utils?
    # Separate this into its own util?
    if shutil.which("cythonize"):
        pyx_dpath = dirname(pyx_fpath)

        # Check if the compiled library exists
        pyx_base = splitext(basename(pyx_fpath))[0]

        SO_EXTS = _platform_pylib_exts()
        so_fname = False
        for fname in os.listdir(pyx_dpath):
            if fname.startswith(pyx_base) and fname.endswith(SO_EXTS):
                so_fname = fname
                break

        try:
            # Currently this functionality depends on ubelt.
            # We could replace ub.cmd with subprocess.check_call and ub.augpath
            # with os.path operations, but hash_file and CacheStamp are harder
            # to replace. We can use "liberator" to statically extract these
            # and add them to nx.utils though.
            import ubelt as ub
        except Exception:
            return False
        else:
            if so_fname is False:
                # We can compute what the so_fname will be if it doesnt exist
                so_fname = pyx_base + SO_EXTS[0]

            so_fpath = join(pyx_dpath, so_fname)
            depends = [ub.hash_file(pyx_fpath, hasher="sha1")]
            stamp_fname = ub.augpath(so_fname, ext=".jit.stamp")
            stamp = ub.CacheStamp(
                stamp_fname,
                dpath=pyx_dpath,
                product=so_fpath,
                depends=depends,
                verbose=verbose,
            )
            if stamp.expired():
                ub.cmd("cythonize -i {}".format(pyx_fpath), verbose=verbose, check=True)
                stamp.renew()
            return True
