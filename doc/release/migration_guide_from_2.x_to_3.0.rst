:orphan:

*****************************
Preparing for the 3.0 release
*****************************

.. note::
   Much of the work leading to the NetworkX 3.0 release will be included
   in the NetworkX 2.6 and 2.7 releases.  For example, we are deprecating a lot
   of old code in the 2.6 and 2.7 releases.  This guide will discuss this
   ongoing work and will help you understand what changes you can make now
   to minimize the disruption caused by the move to 3.0.

This is a guide for people moving from NetworkX 2.X to NetworkX 3.0

Any issues with these can be discussed on the `mailing list
<https://groups.google.com/forum/#!forum/networkx-discuss>`_.

The focus of 3.0 release is on addressing years of technical debt, modernizing our codebase,
improving performance, and making it easier to contribute.
We plan to release 2.7 near the end of summer and 3.0 near the end of the year.

Default dependencies
--------------------

We no longer depend on the "decorator" library.

Deprecated code
---------------

The 2.6 release deprecates over 30 functions.
See :ref:`networkx_2.6`.

---

The functions `read_gpickle` and `write_gpickle` will be removed in 3.0.
You can read and write NetworkX graphs as Python pickles.

>>> import pickle
>>> G = nx.path_graph(4)
>>> with open('test.gpickle', 'wb') as f:
...     pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
... 
>>> with open('test.gpickle', 'rb') as f:
...     G = pickle.load(f)
... 

The functions `read_yaml` and `write_yaml` will be removed in 3.0.
You can read and write NetworkX graphs in YAML format
using pyyaml.

>>> import yaml
>>> G = nx.path_graph(4)
>>> with open('test.yaml', 'w') as f:
...     yaml.dump(G, f)
... 
>>> with open('test.yaml', 'r') as f:
...     G = yaml.load(f, Loader=yaml.Loader)
