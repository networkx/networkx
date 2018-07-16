.. _randomness:

Randomness
==========
.. currentmodule:: networkx

Random Number Generators (RNGs) are often used when generating, drawing
and computing properties or manipulating networks. NetworkX provides
functions which use one of two standard RNGs: NumPy's package `numpy.random`
or Python's built-in package `random`. They each provide the same 
algorithm for generating numbers (Mersenne Twister). Their interfaces
are similar (dangerously similar) and yet distinct. 
They each provide a global default instance of their generator that
is shared by all programs in a single session.
For the most part you can use the RNGs as NetworkX has them set up and
you'll get reasonable pseudorandom results (results that are statistically
random, but created in a deterministic manner). 

Sometimes you want more control over how the numbers are generated.
In particular, you need to set the `seed` of the generator to make
your results reproducible -- either for scientific publication or 
for debugging. Both RNG packages have easy functions to set the seed
to any integer, thus determining the subsequent generated values.
Since this package (and many others) use both RNGs you may need to
set the `seed` of both RNGs.  Even if we strictly only used one of the
RNGs, you may find yourself using another package that uses the other.
Setting the state of the two global RNGs is as simple setting the
seed of each RNG to an arbitrary integer:

.. nbplot::

   >>> import random
   >>> random.seed(246)        # or any integer
   >>> import numpy
   >>> numpy.random.seed(4812)

Many users will be satisfied with this level of control.

For people who want even more control, we include an optional argument
to functions that use an RNG.  This argument is called `seed`, but
determines more than the seed of the RNG. It tells the function which
RNG package to use, and whether to use a global or local RNG.

.. nbplot::

    >>> from networkx import path_graph, random_layout
    >>> G = path_graph(9)
    >>> pos = random_layout(G, seed=None)  # use (either) global default RNG
    >>> pos = random_layout(G, seed=42)  # local RNG just for this call
    >>> pos = random_layout(G, seed=numpy.random)  # use numpy global RNG
    >>> random_state = numpy.random.RandomState(42) 
    >>> pos = random_layout(G, seed=random_state)  # use/reuse your own RNG

Each NetworkX function that uses an RNG was written with one RNG package
in mind. It either uses `random` or `numpy.random` by default.
But some users want to only use a single RNG for all their code.
This `seed` argument provides a mechanism so that any function
can use a `numpy.random` RNG even if the function is written for `random`.
It works as follows.

The default behavior (when `seed=None`) is to use the global RNG
for the function's preferred package. 
If seed is set to an integer value,
a local RNG is created with the indicated seed value and
is used for the duration of that function (including any
calls to other functions) and then discarded.
Alternatively, you can specify `seed=numpy.random` to ensure that
the global numpy RNG is used whether the function expects it or not.
Finally, you can provide a numpy RNG to be used by the function.
The RNG is then available to use in other functions or even other
package like sklearn.
In this way you can use a single RNG for all random numbers 
in your project.

While it is possible to assign `seed` a `random`-style RNG for
NetworkX functions written for the `random` package API,
the numpy RNG interface has too 
many nice features for us to ensure a `random`-style RNG will work in
all functions. In practice, you can do most things using only `random`
RNGs (useful if numpy is not available). But your experience will be
richer if numpy is available.

To summarize, you can easily ignore the `seed` argument and use the global
RNGs. You can specify to use only the numpy global RNG with 
`seed=numpy.random`. You can use a local RNG by providing an integer
seed value. And you can provide your own numpy RNG, reusing it for all
functions. It is easier to use numpy RNGs if you want a single RNG for 
your computations.
