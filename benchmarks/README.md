## NetworkX ASV Benchmarks

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
