"""
===================
Path Correspondence
===================

This example introduces the "maximum common path embedding" problem.

Given two sets of filesystem-like paths, the maximum common path embedding
problems seeks to find the maximium sized correspondence between these sets in
the case where paths in either set may have been given extra prefixes,
suffixes, or had intermediate directories removed.

We will solve this problem via a reduction to the "maximum common path
embedding". We will represent each set of paths as a directed ordered tree and
find the maximum common embedding (i.e. minor) between the two trees subject to
a custom node affinity function. The resulting embedded trees (i.e. minors) can
then be directly converted back to the optimal set of corresponding paths.


Example 1
---------

As a concrete example, imagine you have two computers where the paths on the
first computer are:

>>> paths1 = [  # doctest: +SKIP
...      '/home/wile/project1/main.py',
...      '/home/wile/project2/main.py',
...      '/home/wile/Documents/resume.tex',
...      '/home/wile/Documents/notes.txt',
...      '/home/wile/Documents/tmp.txt',
... ]

And the paths on the second computer are similar, but the projects were moved
into a "code" subfolder, and the user directory is setup differently, and
several files exist only one either the first or the second machine.

>>> paths2 = [  # doctest: +SKIP
...     '/home/local/acme/wile.coyote/code/project1/main.py',
...     '/home/local/acme/wile.coyote/code/project2/main.py',
...     '/home/local/acme/wile.coyote/code/project3/main.py',
...     '/home/local/acme/wile.coyote/Documents/resume.tex',
... ]

A maximum path embedding would locate the correspondence between
``paths1`` and ``paths2`` as follows:

>>> {  # doctest: +SKIP
...     '/home/wile/project1/main.py': '/home/local/acme/wile.coyote/code/project1/main.py',
...     '/home/wile/project2/main.py': '/home/local/acme/wile.coyote/code/project2/main.py',
...     '/home/wile/Documents/resume.tex': '/home/local/acme/wile.coyote/Documents/resume.tex',
... }


Example 2
---------

Another application of the "maximum common path embedding" occurs when
transfering weights between PyTorch neural network. When training neural
networks it is common to train a core "backbone" network on some classification
task and then use those weights as a component in a larger network for a more
complex task.

Weights in a torch network are specified using a path-like structure using "."
as the separator instead of "/". The layer-names for a simple classification
"backbone" network might look like:

>>> backbone_layers = [  # doctest: +SKIP
...     'conv1.weight',
...     'layer1.0.conv1.weight',
...     'layer1.0.bn1.running_mean',
...     'layer1.0.bn1.running_var',
...     'layer1.0.bn1.num_batches_tracked',
...     'layer1.0.conv2.weight',
...     'layer1.0.downsample.0.weight',
...     'layer2.0.conv1.weight',
...     'layer2.0.conv2.weight',
...     'layer2.0.conv3.weight',
...     'layer3.0.conv1.weight',
...     'fc.weight',
...     'fc.bias',
... ]

Parts of this "backbone" might then be used in as components in a more complex
architecture that looks like:

>>> model_layers = [  # doctest: +SKIP
...     'preproc.conv1.weight',
...     'backbone.layer1.0.conv1.weight',
...     'backbone.layer1.0.bn1.running_mean',
...     'backbone.layer1.0.bn1.running_var',
...     'backbone.layer1.0.conv2.weight',
...     'backbone.layer1.0.downsample.0.weight',
...     'backbone.layer2.0.conv1.weight',
...     'backbone.layer2.0.conv2.weight',
...     'backbone.layer2.0.conv3.weight',
...     'backbone.layer3.0.conv1.weight',
...     'head.conv1',
...     'head.conv2',
...     'head.fc.weight',
...     'head.fc.bias',
... ]

To correctly load the weights, we need to create a correspondence between the
layers in the backbone and the layers in the model.  Usually, this would be
hard coded by a developer, but we can do better by using a "maximum common path
embedding". For this example the computed correspondence is:

>>> {  # doctest: +SKIP
...     'conv1.weight': 'preproc.conv1.weight',
...     'layer1.0.conv1.weight': 'backbone.layer1.0.conv1.weight',
...     'layer1.0.bn1.running_mean': 'backbone.layer1.0.bn1.running_mean',
...     'layer1.0.bn1.running_var': 'backbone.layer1.0.bn1.running_var',
...     'layer1.0.conv2.weight': 'backbone.layer1.0.conv2.weight',
...     'layer1.0.downsample.0.weight': 'backbone.layer1.0.downsample.0.weight',
...     'layer2.0.conv1.weight': 'backbone.layer2.0.conv1.weight',
...     'layer2.0.conv2.weight': 'backbone.layer2.0.conv2.weight',
...     'layer2.0.conv3.weight': 'backbone.layer2.0.conv3.weight',
...     'layer3.0.conv1.weight': 'backbone.layer3.0.conv1.weight',
...     'fc.weight': 'head.fc.weight',
...     'fc.bias': 'head.fc.bias',
... }


Algorithm Overview
------------------

The code in this file demonstrates for how to implement a solution to the
"maximum common path embedding" problem using a reduction to the "maximum
common ordered tree embedding" problem.  The basic outline of the algorithm is:


1. Convert each set of paths into an ordered directed tree.
   By defining a path separator (e.g. "/" or ".") we can add directory as a
   node in the tree. The value of the node is the absolute path to the
   directory. A directed edge is placed between a directory and each of its
   contents. Each leaf node in this tree corresponds to an original path item.

   For instance, the tree for the first 5 layers of ``backbone_layers`` in
   Example 2 would look like:

    >>> ...  # doctest: +SKIP
    ╟── ('conv1',)
    ╎   └─╼ ('conv1', 'weight')
    ╟── ('layer1',)
    ╎   └─╼ ('layer1', '0')
    ╎       ├─╼ ('layer1', '0', 'conv1')
    ╎       │   └─╼ ('layer1', '0', 'conv1', 'weight')
    ╎       ├─╼ ('layer1', '0', 'bn1')
    ╎       │   ├─╼ ('layer1', '0', 'bn1', 'running_mean')
    ╎       │   ├─╼ ('layer1', '0', 'bn1', 'running_var')
    ╎       │   └─╼ ('layer1', '0', 'bn1', 'num_batches_tracked')

2. Define a custom ``node_affinity`` function.
   The affinity between two nodes indicates both if they are able to match and
   how good the match is. For our problem we only want paths to be able to
   match if the final component of the paths are the same (e.g. Any path ending
   in ``weight`` should be able to match any other path ending in ``weight``).
   However, we do want to encourage matching between paths with more trailing
   components in common to match with higer priority. (e.g.
   ``backbone.layer1.0.conv1.weight`` should prefer matching
   ``layer1.0.conv1.weight`` over ``backbone.layer2.0.conv1.weight``).
   Thus we define our affinity score between two nodes to be the number of
   contiguous trailing components in common.

3. Use :func:`networkx.algorithms.minors.tree_embedding.maximum_common_ordered_subtree_embedding`
   to find the maximum subtree embeddings subject to our node affinity
   function.

4. Convert the corresponding subtree embeddings back to paths by taking the
   values of the leaf nodes. These lists of paths is the the maximum weight
   correspondence.


Benchmarks
----------

In addition to an example implementation for the path embedding problem this
file also includes a set of benchmarks demonstrating runtime differences for
different backend modes of the
:func:`networkx.algorithms.string.balanced_sequence.longest_common_balanced_embedding`
algorithm, which is the core workhorse used to solve this problem. We use the
:func:`random_paths` function defined here to simulate various conditions that
may arise in real-world applications.
"""

__devnotes__ = """
Command Line
------------
# Run tests and doctests
pytest examples/applications/path_correspondence.py -s -v --doctest-modules

# Run benchmark (requires timerit and ubelt module)
xdoctest -m examples/applications/path_correspondence.py bench_maximum_common_path_embedding

# Run main function
python examples/applications/path_correspondence.py
"""
import networkx as nx
import pprint
from networkx.algorithms.minors import maximum_common_ordered_subtree_embedding


def maximum_common_path_embedding(
    paths1, paths2, sep="/", impl="auto", item_type="auto"
):
    """
    Finds the maximum path embedding common between two sets of paths

    Parameters
    ----------
    paths1, paths2: List[str]
        a list of ordered paths

    sep: str
        path separator character

    impl: str
        backend runtime to use

    item_type: str
        backend representation to use

    Returns
    -------
    Tuple[List[str], List[str]]
        corresponding lists subpaths1 and subpaths2 which are subsets of paths1
        and path2 respectively

    Examples
    --------
    >>> paths1 = [
    ...     '/usr/bin/python',
    ...     '/usr/bin/python3.6.1',
    ...     '/usr/lib/python3.6/dist-packages/networkx',
    ...     '/usr/lib/python3.6/dist-packages/numpy',
    ...     '/usr/include/python3.6/Python.h',
    ... ]
    >>> paths2 = [
    ...     '/usr/local/bin/python',
    ...     '/usr/bin/python3.6.2',
    ...     '/usr/local/lib/python3.6/dist-packages/networkx',
    ...     '/usr/local/lib/python3.6/dist-packages/scipy',
    ...     '/usr/local/include/python3.6/Python.h',
    ... ]
    >>> subpaths1, subpaths2 = maximum_common_path_embedding(paths1, paths2)
    >>> import pprint
    >>> print('subpaths1 = {}'.format(pprint.pformat(subpaths1)))
    subpaths1 = ['/usr/bin/python',
     '/usr/lib/python3.6/dist-packages/networkx',
     '/usr/include/python3.6/Python.h']
    >>> print('subpaths2 = {}'.format(pprint.pformat(subpaths2)))
    subpaths2 = ['/usr/local/bin/python',
     '/usr/local/lib/python3.6/dist-packages/networkx',
     '/usr/local/include/python3.6/Python.h']
    """
    # the longest common balanced sequence problem
    def _affinity(node1, node2):
        # The default node affinity is the number of contiguous trailing
        # components in common.
        score = 0
        for t1, t2 in zip(node1[::-1], node2[::-1]):
            if t1 == t2:
                score += 1
            else:
                break
        return score

    node_affinity = _affinity

    tree1 = paths_to_otree(paths1, sep=sep)
    tree2 = paths_to_otree(paths2, sep=sep)

    subtree1, subtree2, _ = maximum_common_ordered_subtree_embedding(
        tree1, tree2, node_affinity=node_affinity, impl=impl, item_type=item_type
    )

    subpaths1 = [
        sep.join(node) for node in subtree1.nodes if subtree1.out_degree[node] == 0
    ]
    subpaths2 = [
        sep.join(node) for node in subtree2.nodes if subtree2.out_degree[node] == 0
    ]
    return subpaths1, subpaths2


def paths_to_otree(paths, sep="/"):
    """
    Generates an ordered tree from a list of path strings

    Parameters
    ----------
    paths: List[str]
        a list of paths

    sep : str
        path separation character. defaults to "/"

    Returns
    -------
    nx.OrderedDiGraph

    Example
    -------
    >>> from networkx.readwrite.text import forest_str
    >>> paths = [
    ...     '/etc/ld.so.conf',
    ...     '/usr/bin/python3.6',
    ...     '/usr/include/python3.6/Python.h',
    ...     '/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu/libpython3.6.so',
    ...     '/usr/local/bin/gnumake.h',
    ...     '/usr/local/etc',
    ...     '/usr/local/lib/python3.6/dist-packages',
    ... ]
    >>> otree = paths_to_otree(paths)
    >>> print(forest_str(otree, with_labels=True))
    ╙── /
        ├─╼ etc
        │   └─╼ ld.so.conf
        └─╼ usr
            ├─╼ bin
            │   └─╼ python3.6
            ├─╼ include
            │   └─╼ python3.6
            │       └─╼ Python.h
            ├─╼ lib
            │   └─╼ python3.6
            │       └─╼ config-3.6m-x86_64-linux-gnu
            │           └─╼ libpython3.6.so
            └─╼ local
                ├─╼ bin
                │   └─╼ gnumake.h
                ├─╼ etc
                └─╼ lib
                    └─╼ python3.6
                        └─╼ dist-packages

    >>> # Demo the actual node structure by printing without labels
    >>> from networkx.readwrite.text import forest_str
    >>> paths = [
    ...     '1/1/2',
    ...     '1/3/2',
    ...     '1/3/3',
    ...     '1/2',
    ... ]
    >>> otree = paths_to_otree(paths)
    >>> print(forest_str(otree, with_labels=False))
    ╙── ('1',)
        ├─╼ ('1', '1')
        │   └─╼ ('1', '1', '2')
        ├─╼ ('1', '3')
        │   ├─╼ ('1', '3', '2')
        │   └─╼ ('1', '3', '3')
        └─╼ ('1', '2')
    """
    otree = nx.OrderedDiGraph()
    for path in paths:
        parts = tuple(path.split(sep))
        node_path = []

        for i in range(1, len(parts) + 1):
            node = parts[0:i]
            otree.add_node(node)
            # Add each node name as a label for nicer printing
            otree.nodes[node]["label"] = node[-1]
            node_path.append(node)

        for edge in zip(node_path[:-1], node_path[1:]):
            otree.add_edge(*edge)

    if ("",) in otree.nodes:
        otree.nodes[("",)]["label"] = sep
    return otree


def random_paths(
    size=10,
    max_depth=10,
    common=0,
    prefix_depth1=0,
    prefix_depth2=0,
    sep="/",
    labels=26,
    seed=None,
):
    """
    Returns two randomly created paths (as in directory structures) for use in
    testing and benchmarking :func:`maximum_common_path_embedding`.

    Parameters
    ----------
    size : int
        The number of independant random paths

    max_depth : int
        Maximum depth for the independant random paths

    common : int
        The number of shared common paths

    prefix_depth1: int
        Depth of the random prefix attacheded to first common paths

    prefix_depth2: int
        Depth of the random prefix attacheded to second common paths

    labels: int or collection
        Number of or collection of tokens that can be used as node labels

    sep: str
        path separator

    seed:
        Random state or seed

    Returns
    -------
    paths1, paths2: Tuple[List[str], List[str]]
        Two sets of paths with some degree of common embedded structure

    Examples
    --------
    >>> from networkx.algorithms.minors.tree_embedding import tree_to_seq
    >>> paths1, paths2 = random_paths(
    ...     size=3, max_depth=3, common=3,
    ...     prefix_depth1=3, prefix_depth2=3, labels=2 ** 16,
    ...     seed=0)
    >>> tree = paths_to_otree(paths1)
    >>> seq = tree_to_seq(tree, item_type='chr')[0]
    >>> seq = tree_to_seq(tree, item_type='number')[0]
    >>> import pprint
    >>> print('paths1 = {}'.format(pprint.pformat(paths1)))
    paths1 = ['brwb/eaaw/druy/ctge/dyaj/vcy',
     'brwb/eaaw/druy/dqbh/cqht',
     'brwb/eaaw/druy/plp',
     'dnfa/img',
     'dyxs/dacf',
     'ebwq/djxa']
    >>> print('paths2 = {}'.format(pprint.pformat(paths2)))
    paths2 = ['buug/befe/cjcq',
     'ccnj/bfum/cpbb',
     'ceps/nbn/cxp/ctge/dyaj/vcy',
     'ceps/nbn/cxp/dqbh/cqht',
     'ceps/nbn/cxp/plp',
     'twe']
    """
    from networkx.utils import create_py_random_state

    rng = create_py_random_state(seed)

    if isinstance(labels, int):
        alphabet = list(map(chr, range(ord("a"), ord("z"))))

        def random_label():
            digit = rng.randint(0, labels)
            label = _convert_digit_base(digit, alphabet)
            return label

    else:
        from functools import partial

        random_label = partial(rng.choice, labels)

    def random_path(rng, max_depth):
        depth = rng.randint(1, max_depth)
        parts = [str(random_label()) for _ in range(depth)]
        path = sep.join(parts)
        return path

    # These paths might be shared (but usually not)
    iid_paths1 = {random_path(rng, max_depth) for _ in range(size)}
    iid_paths2 = {random_path(rng, max_depth) for _ in range(size)}

    # These paths will be shared
    common_paths = {random_path(rng, max_depth) for _ in range(common)}

    if prefix_depth1 > 0:
        prefix1 = random_path(rng, prefix_depth1)
        common1 = {sep.join([prefix1, suff]) for suff in common_paths}
    else:
        common1 = common_paths

    if prefix_depth2 > 0:
        prefix2 = random_path(rng, prefix_depth2)
        common2 = {sep.join([prefix2, suff]) for suff in common_paths}
    else:
        common2 = common_paths

    paths1 = sorted(common1 | iid_paths1)
    paths2 = sorted(common2 | iid_paths2)

    return paths1, paths2


def _convert_digit_base(digit, alphabet):
    """
    Helper for random_paths

    Parameters
    ----------
    digit : int
        number in base 10 to convert

    alphabet : list
        symbols of the conversion base
    """
    baselen = len(alphabet)
    x = digit
    if x == 0:
        return alphabet[0]
    sign = 1 if x > 0 else -1
    x *= sign
    digits = []
    while x:
        digits.append(alphabet[x % baselen])
        x //= baselen
    if sign < 0:
        digits.append("-")
    digits.reverse()
    newbase_str = "".join(digits)
    return newbase_str


def bench_maximum_common_path_embedding():
    """
    Runs algorithm benchmarks over a range of parameters.

    Running this benchmark does require some external libraries

    Requirements
    ------------
    timerit >= 0.3.0
    ubelt >= 0.9.2

    Command Line
    ------------
    xdoctest -m examples/applications/path_correspondence.py bench_maximum_common_path_embedding
    """
    import itertools as it
    import ubelt as ub
    import timerit
    from networkx.algorithms.string import balanced_sequence

    data_modes = []

    available_impls = (
        balanced_sequence.available_impls_longest_common_balanced_embedding()
    )

    # Define which implementations we are going to test
    run_basis = {
        "item_type": ["chr", "number"],
        "impl": available_impls,
    }

    # Define the properties of the random data we are going to test on
    data_basis = {
        "size": [20, 50],
        "max_depth": [8, 16],
        "common": [8, 16],
        "prefix_depth1": [0, 4],
        "prefix_depth2": [0, 4],
        # 'labels': [26 ** 1, 26 ** 8]
        "labels": [1, 26],
    }

    # run_basis['impl'] = set(run_basis['impl']) & {
    #     'iter-cython',
    #     'iter',
    # }

    # TODO: parametarize demo names
    # BENCH_MODE = None
    BENCH_MODE = "small"
    # BENCH_MODE = "medium"
    # BENCH_MODE = 'large'

    if BENCH_MODE == "small":
        data_basis = {
            "size": [30],
            "max_depth": [8, 2],
            "common": [2, 8],
            "prefix_depth1": [0, 4],
            "prefix_depth2": [0],
            "labels": [4],
        }
        # run_basis["impl"] = ub.oset(available_impls) - {"recurse"}
        # run_basis["item_type"] = ["number", "chr"]
        # runparam_to_time = {
        #     ('chr', 'iter-cython')       : {'mean': 0.036, 'max': 0.094},
        #     ('chr', 'iter')              : {'mean': 0.049, 'max': 0.125},
        #     ('number', 'iter-cython')    : {'mean': 0.133, 'max': 0.363},
        #     ('number', 'iter')           : {'mean': 0.149, 'max': 0.408},
        # }

    if BENCH_MODE == "medium":
        data_basis = {
            "size": [30, 40],
            "max_depth": [4, 8],
            "common": [8, 50],
            "prefix_depth1": [0, 4],
            "prefix_depth2": [2],
            "labels": [8, 1],
        }
        # Results
        # runparam_to_time = {
        #     ('chr', 'iter-cython')    : {'mean': 0.112, 'max': 0.467},
        #     ('chr', 'iter')           : {'mean': 0.155, 'max': 0.661},
        # }

    if BENCH_MODE == "large":
        data_basis = {
            "size": [30, 40],
            "max_depth": [4, 12],  # 64000
            "common": [8, 32],
            "prefix_depth1": [0, 4],
            "prefix_depth2": [2],
            "labels": [8],
        }
        run_basis["impl"] = available_impls
        # runparam_to_time = {
        #     ('chr', 'iter-cython')    : {'mean': 0.282, 'max': 0.923},
        #     ('chr', 'iter')           : {'mean': 0.409, 'max': 1.328},
        # }

    elif BENCH_MODE == "too-big":
        data_basis = {
            "size": [100],
            "max_depth": [8],
            "common": [80],
            "prefix_depth1": [4],
            "prefix_depth2": [2],
            "labels": [8],
        }

    data_modes = [
        dict(zip(data_basis.keys(), vals)) for vals in it.product(*data_basis.values())
    ]
    run_modes = [
        dict(zip(run_basis.keys(), vals)) for vals in it.product(*run_basis.values())
    ]

    print("len(data_modes) = {!r}".format(len(data_modes)))
    print("len(run_modes) = {!r}".format(len(run_modes)))
    print("total = {}".format(len(data_modes) * len(run_modes)))

    seed = 0
    for idx, datakw in enumerate(data_modes):
        print("datakw = {}".format(ub.repr2(datakw, nl=1)))
        _datakw = ub.dict_diff(datakw, {"complexity"})
        paths1, paths2 = random_paths(seed=seed, **_datakw)
        tree1 = paths_to_otree(paths1)
        tree2 = paths_to_otree(paths2)
        stats1 = {
            "npaths": len(paths1),
            "n_nodes": len(tree1.nodes),
            "n_edges": len(tree1.edges),
            "n_leafs": len([n for n in tree1.nodes if len(tree1.succ[n]) == 0]),
            "depth": max(len(p.split("/")) for p in paths1),
        }
        stats2 = {
            "npaths": len(paths2),
            "n_nodes": len(tree2.nodes),
            "n_edges": len(tree2.edges),
            "n_leafs": len([n for n in tree2.nodes if len(tree2.succ[n]) == 0]),
            "depth": max(len(p.split("/")) for p in paths2),
        }
        complexity = (
            stats1["n_nodes"]
            * min(stats1["n_leafs"], stats1["depth"])
            * stats2["n_nodes"]
            * min(stats2["n_leafs"], stats2["depth"])
        ) ** 0.25

        datakw["complexity"] = complexity
        print("datakw = {}".format(ub.repr2(datakw, nl=0, precision=2)))

        print("stats1 = {}".format(ub.repr2(stats1, nl=0)))
        print("stats2 = {}".format(ub.repr2(stats2, nl=0)))

    total = len(data_modes) * len(run_modes)
    print("len(data_modes) = {!r}".format(len(data_modes)))
    print("len(run_modes) = {!r}".format(len(run_modes)))
    print("total = {!r}".format(total))
    seed = 0

    prog = ub.ProgIter(total=total, verbose=3)
    prog.begin()
    results = []
    ti = timerit.Timerit(1, bestof=1, verbose=1, unit="s")
    for datakw in data_modes:
        _datakw = ub.dict_diff(datakw, {"complexity"})
        paths1, paths2 = random_paths(seed=seed, **_datakw)
        print("---")
        prog.step(4)
        tree1 = paths_to_otree(paths1)
        tree2 = paths_to_otree(paths2)
        stats1 = {
            "npaths": len(paths1),
            "n_nodes": len(tree1.nodes),
            "n_edges": len(tree1.edges),
            "n_leafs": len([n for n in tree1.nodes if len(tree1.succ[n]) == 0]),
            "depth": max(len(p.split("/")) for p in paths1),
        }
        stats2 = {
            "npaths": len(paths2),
            "n_nodes": len(tree2.nodes),
            "n_edges": len(tree2.edges),
            "n_leafs": len([n for n in tree2.nodes if len(tree2.succ[n]) == 0]),
            "depth": max(len(p.split("/")) for p in paths2),
        }
        complexity = (
            stats1["n_nodes"]
            * min(stats1["n_leafs"], stats1["depth"])
            * stats2["n_nodes"]
            * min(stats2["n_leafs"], stats2["depth"])
        ) ** 0.25

        datakw["complexity"] = complexity
        print("datakw = {}".format(ub.repr2(datakw, nl=0, precision=2)))

        if True:
            # idx + 4 > len(data_modes):
            print("stats1 = {}".format(ub.repr2(stats1, nl=0)))
            print("stats2 = {}".format(ub.repr2(stats2, nl=0)))
        for runkw in run_modes:
            paramkw = {**datakw, **runkw}
            run_key = ub.repr2(
                paramkw,
                sep="",
                itemsep="",
                kvsep="",
                explicit=1,
                nobr=1,
                nl=0,
                precision=1,
            )
            try:
                for timer in ti.reset(run_key):
                    with timer:
                        maximum_common_path_embedding(paths1, paths2, **runkw)
            except RecursionError as ex:
                print("ex = {!r}".format(ex))
                row = paramkw.copy()
                row["time"] = float("nan")
            else:
                row = paramkw.copy()
                row["time"] = ti.min()
            results.append(row)
    prog.end()

    print(ub.repr2(ub.sorted_vals(ti.measures["min"]), nl=1, align=":", precision=6))

    import pandas as pd
    import kwarray

    df = pd.DataFrame.from_dict(results)

    dataparam_to_time = {}
    for item_type, subdf in df.groupby(["complexity"] + list(data_basis.keys())):
        stats = kwarray.stats_dict(subdf["time"])
        stats.pop("min", None)
        stats.pop("std", None)
        stats.pop("shape", None)
        dataparam_to_time[item_type] = stats
    dataparam_to_time = ub.sorted_vals(dataparam_to_time, key=lambda x: x["max"])
    print(
        "dataparam_to_time = {}".format(
            ub.repr2(dataparam_to_time, nl=1, precision=3, align=":")
        )
    )
    print(list(data_basis.keys()))

    runparam_to_time = {}
    for item_type, subdf in df.groupby(["item_type", "impl"]):
        stats = kwarray.stats_dict(subdf["time"])
        stats.pop("min", None)
        stats.pop("std", None)
        stats.pop("shape", None)
        runparam_to_time[item_type] = stats
    runparam_to_time = ub.sorted_vals(runparam_to_time, key=lambda x: x["max"])
    print(
        "runparam_to_time = {}".format(
            ub.repr2(runparam_to_time, nl=1, precision=3, align=":")
        )
    )


# -- tests


def test_simple_cases():
    print("--- Test Simple Cases ---")
    paths1 = ["foo/bar"]
    paths2 = ["baz/biz"]
    embedding1, embedding2 = maximum_common_path_embedding(paths1, paths2)
    assert len(embedding1) == 0
    assert len(embedding2) == 0

    # test_compatable():
    paths1 = ["root/suffix1"]
    paths2 = ["root/suffix2"]
    embedding1, embedding2 = maximum_common_path_embedding(paths1, paths2)
    assert embedding1 == ["root"]
    assert embedding2 == ["root"]

    paths1 = ["root/suffix1"]
    paths2 = ["root"]
    embedding1, embedding2 = maximum_common_path_embedding(paths1, paths2)
    assert embedding1 == ["root"]
    assert embedding2 == ["root"]

    # test_prefixed():
    paths1 = ["prefix1/root/suffix1"]
    paths2 = ["root/suffix2"]
    embedding1, embedding2 = maximum_common_path_embedding(paths1, paths2)
    assert embedding1 == ["prefix1/root"]
    assert embedding2 == ["root"]

    paths1 = ["prefix1/root/suffix1"]
    paths2 = ["prefix1/root/suffix2"]
    embedding1, embedding2 = maximum_common_path_embedding(paths1, paths2)
    assert embedding1 == ["prefix1/root"]
    assert embedding2 == ["prefix1/root"]

    # test_simple1():
    paths1 = [
        "root/file1",
        "root/file2",
        "root/file3",
    ]
    paths2 = [
        "prefix1/root/file1",
        "prefix1/root/file2",
        "root/file3",
    ]
    embedding1, embedding2 = maximum_common_path_embedding(paths1, paths2)
    assert embedding1 == paths1
    assert embedding2 == paths2

    paths1 = [
        "root/file1",
        "root/file2",
        "root/file3",
    ]
    paths2 = [
        "prefix1/root/file1",
        "prefix1/root/file2",
        "prefix2/root/file3",
        "prefix2/root/file4",
    ]
    embedding1, embedding2 = maximum_common_path_embedding(paths1, paths2)
    assert embedding1 == paths1


def _demodata_resnet_module_state(arch):
    """
    Construct paths corresponding to resnet convnet state keys to
    simulate a real world use case for path-embeddings.

    Ignore
    ------
    # Check to make sure the demodata agrees with real data
    import torchvision
    paths_true = list(torchvision.models.resnet50().state_dict().keys())
    paths_demo = _demodata_resnet_module_state('resnet50')
    print(ub.hzcat([ub.repr2(paths_true, nl=2), ub.repr2(paths_demo)]))
    assert paths_demo == paths_true

    paths_true = list(torchvision.models.resnet18().state_dict().keys())
    paths_demo = _demodata_resnet_module_state('resnet18')
    print(ub.hzcat([ub.repr2(paths_true, nl=2), ub.repr2(paths_demo)]))
    assert paths_demo == paths_true

    paths_true = list(torchvision.models.resnet152().state_dict().keys())
    paths_demo = _demodata_resnet_module_state('resnet152')
    print(ub.hzcat([ub.repr2(paths_true, nl=2), ub.repr2(paths_demo)]))
    assert paths_demo == paths_true
    """
    if arch == "resnet18":
        block_type = "basic"
        layer_blocks = [2, 2, 2, 2]
    elif arch == "resnet50":
        block_type = "bottleneck"
        layer_blocks = [3, 4, 6, 3]
    elif arch == "resnet152":
        block_type = "bottleneck"
        layer_blocks = [3, 8, 36, 3]
    else:
        raise KeyError(arch)
    paths = []
    paths += [
        "conv1.weight",
        "bn1.weight",
        "bn1.bias",
        "bn1.running_mean",
        "bn1.running_var",
        "bn1.num_batches_tracked",
    ]
    if block_type == "bottleneck":
        num_convs = 3
    elif block_type == "basic":
        num_convs = 2
    else:
        raise KeyError(block_type)

    for layer_idx, nblocks in enumerate(layer_blocks, start=1):
        for block_idx in range(0, nblocks):
            prefix = "layer{}.{}.".format(layer_idx, block_idx)

            for conv_idx in range(1, num_convs + 1):
                paths += [
                    prefix + "conv{}.weight".format(conv_idx),
                    prefix + "bn{}.weight".format(conv_idx),
                    prefix + "bn{}.bias".format(conv_idx),
                    prefix + "bn{}.running_mean".format(conv_idx),
                    prefix + "bn{}.running_var".format(conv_idx),
                    prefix + "bn{}.num_batches_tracked".format(conv_idx),
                ]
            if block_idx == 0 and layer_idx > 0:
                if block_type != "basic" or layer_idx > 1:
                    paths += [
                        prefix + "downsample.0.weight",
                        prefix + "downsample.1.weight",
                        prefix + "downsample.1.bias",
                        prefix + "downsample.1.running_mean",
                        prefix + "downsample.1.running_var",
                        prefix + "downsample.1.num_batches_tracked",
                    ]
    paths += [
        "fc.weight",
        "fc.bias",
    ]
    return paths


def test_realworld_case1():
    """
    In this example we take standard layer names for a torchvision ResNet50 and
    prefix them with the "module." prefix that is commonly exported with torch
    state dictionaries when using ``torch.nn.DataParallel``. This optimal
    soltion in this case is to simply remove the module prefix, which our
    algorithm does nicely.

    Ignore
    ------
    import torchvision
    paths1 = list(torchvision.models.resnet50().state_dict().keys())
    print(ub.hzcat(['paths1 = {}'.format(ub.repr2(paths1, nl=2)), ub.repr2(paths)]))
    len(paths1)
    """
    print("--- Test Real World Case 1 ---")
    # times: resnet18:  0.16 seconds
    # times: resnet50:  0.93 seconds
    # times: resnet152: 9.83 seconds
    paths1 = _demodata_resnet_module_state("resnet50")
    paths2 = ["module." + p for p in paths1]

    print("[dst] paths1 = {}".format(pprint.pformat(paths1)))
    print("[src] paths2 = {}".format(pprint.pformat(paths1)))

    embedding1, embedding2 = maximum_common_path_embedding(paths1, paths2, sep=".")

    mapping = dict(zip(embedding1, embedding2))
    print("mapping = {}".format(pprint.pformat(mapping, sort_dicts=False)))

    assert [p[len("module.") :] for p in embedding2] == embedding1


def test_realworld_case2():
    """
    In this example we take standard layer names for a torchvision ResNet18
    neural network and embed it within a set of layer names you may see in an
    object detection model. We also add the "module." prefix to the ResNet18
    weights.  The optimal solution for this network will be to remove the
    "module." prefix in the backbone layer names and the "detector.backbone."
    prefix in the detector layer names. The algorithm must also handle the fact
    that not all of the backbone layers are used in the detector and that the
    detector has extra layers that do not correspond to the backbone.

    Ignore
    ------
    import torchvision
    paths1 = list(torchvision.models.resnet152().state_dict().keys())
    print('paths1 = {}'.format(ub.repr2(paths1, nl=2)))
    """
    print("--- Test Real World Case 2 ---")

    backbone = _demodata_resnet_module_state("resnet18")

    # Detector strips of prefix and suffix of the backbone net
    subpaths = ["detector.backbone." + p for p in backbone[6:-2]]
    paths1 = (
        [
            "detector.conv1.weight",
            "detector.bn1.weight",
            "detector.bn1.bias",
        ]
        + subpaths
        + [
            "detector.head1.conv1.weight",
            "detector.head1.conv2.weight",
            "detector.head1.conv3.weight",
            "detector.head1.fc.weight",
            "detector.head1.fc.bias",
            "detector.head2.conv1.weight",
            "detector.head2.conv2.weight",
            "detector.head2.conv3.weight",
            "detector.head2.fc.weight",
            "detector.head2.fc.bias",
        ]
    )
    paths2 = ["module." + p for p in backbone]

    print("[backbone] paths1 = {}".format(pprint.pformat(paths1)))
    print("[model]    paths2 = {}".format(pprint.pformat(paths1)))

    embedding1, embedding2 = maximum_common_path_embedding(paths1, paths2, sep=".")

    mapping = dict(zip(embedding1, embedding2))
    print("mapping = {}".format(pprint.pformat(mapping, sort_dicts=False)))

    # Note in the embedding case there may be superfluous assignments
    # but they can either be discarded in post-processing or they wont
    # be in the solution if we use isomorphisms instead of embeddings
    assert len(subpaths) < len(mapping), "all subpaths should be in the mapping"

    non_common1 = set(paths1) - set(embedding1)
    non_common2 = set(paths2) - set(embedding2)

    assert non_common2 == {
        "module.bn1.num_batches_tracked",
        "module.bn1.running_mean",
        "module.bn1.running_var",
    }

    assert non_common1 == {
        "detector.head1.conv1.weight",
        "detector.head1.conv2.weight",
        "detector.head1.conv3.weight",
        "detector.head1.fc.bias",
        "detector.head1.fc.weight",
        "detector.head2.conv1.weight",
        "detector.head2.conv2.weight",
        "detector.head2.conv3.weight",
    }


def main():
    import sys

    test_simple_cases()
    print("\n\n")
    test_realworld_case1()
    print("\n\n")
    test_realworld_case2()

    if "--bench" in sys.argv:
        bench_maximum_common_path_embedding()


if __name__ == "__main__":
    main()
