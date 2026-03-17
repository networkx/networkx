# NetworkX ASV Benchmarks

NetworkX uses [`asv`](https://asv.readthedocs.io/en/latest/) to monitor for
performance regressions and evaluate proposals for improved performance.
Available benchmarks are available in the `benchmarks/benchmarks` subdirectory
and are loosely organized/named to reflect either the algorithms or data structures
that they focus on.

The two most generic sets of benchmarks are:

- `benchmarks_classes.py`: This covers benchmarks for performance of core
  NetworkX classes (`Graph`, `DiGraph`, `MultiGraph`, `MultiDiGraph`).
  We test performance of basic graph operations (`add_node`, `add_edge`, `subgraph`
  and others). Code that touches the core classes should run these benchmarks
  to make sure if there is a performance hit or gain.
- `benchmark_algorithms.py`: This runs a tiny subset of algorithms which cover
  different parts of our codebase. We use graphs with different density, and a
  real world dataset from SNAP datasets to run the algorithms.

There are many other algorithms captured in other files/benchmarking classes
within the suite.

## Setup and configuration

Benchmarking runs are controlled by the `asv.conf.json` configuration file.
For a full listing of configuration options, see
[the `asv` documentation](https://asv.readthedocs.io/en/latest/asv.conf.json.html#conf-reference)

Typically, the most important configuration options for a successful ASV
configuration are:

1. `environment_type` which controls the environment management tool used
   by ASV,
2. `pythons`, specifying which version(s) of Python will be used during
   benchmarking, and
3. `matrix` which dictates what dependencies (and their versions) will be
   tested against.

`environment_type` is set to `"conda"` by default - the `"virtualenv"` option
is recommended for simpler building/setup.

```{note}
When using `environment_type: "virtualenv"`, it is recommended to limit the
`pythons` field to only those versions of Python that are installed on the
system.
```

The `matrix` field dictates which optional dependencies will be installed in the
benchmarking environment.
To get an accurate picture of NetworkX performance with "default" soft dependencies
installed, be sure to include `numpy` and `scipy` in this listing.
To evaluate pure-Python code branches, remove the dependencies from `matrix`.

```{note}
Some benchmarks themselves depend on `numpy`, `scipy` and/or `pandas`; so removing
dependencies may cause some benchmarks to be skipped.
```

### Example configuration options

The default configuration builds benchmarking environments for 3 different
versions of Python, all with the latest stable version of default dependencies,
using `conda` for managing the build environment and Python versions.

To switch to built-in environment management:

```yaml
"environment_type": "virtualenv"
```

To limit the benchmarking run to a single version of Python:

```yaml
"pythons": ["3.13"]
```

## Running the benchmark suite

To run the benchmark on the current HEAD commit:

```
asv run
```

Run the benchmark to compare two commits:

```
asv continuous base_commit_hash test_commit_hash
```

The `--bench` flag can be used to limit a run to a subset of benchmarks.
For example, the following will only run the algorithm benchmarks for performance
comparison between two commits:

```
asv continuous --bench AlgorithmBenchmarks <sha1> <sha2>
```

The same pattern can be used to specify individual benchmarks:

```
asv continuous --bench AlgorithmBenchmarks.time_pagerank <sha1> <sha2>
```

To know more visit - https://asv.readthedocs.io/en/stable/commands.html
