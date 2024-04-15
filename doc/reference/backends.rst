********************
Backends and Configs
********************

.. note:: Both NetworkX backend and config systems are experimental. Backends
   let you execute an alternative backend implementation instead of NetworkX's
   pure Python dictionaries implementation. The config system provides library level
   storage of configuration settings that otherwise might come from environment
   variables. Both of these systems are experimental and details will almost
   certainly change in future releases!

Backends
--------
.. automodule:: networkx.utils.backends

.. autosummary::
   :toctree: generated/

   _dispatchable

Configs
-------
.. automodule:: networkx.utils.configs

.. autoclass:: config
.. autoclass:: NetworkXConfig
.. autoclass:: Config
