**********************************
Experimental: Backends and Configs
**********************************

.. note:: Both NetworkX backend and config systems are experimental. Backends
   let you execute an alternative backend implementation instead of NetworkX's
   pure Python dictionaries implementation. These things will almost certainly
   change and break in the future releases!

Backends
--------
.. automodule:: networkx.utils.backends

Decorator: _dispatchable
------------------------
.. autodecorator:: _dispatchable

Configs
-------
.. automodule:: networkx.utils.configs

.. autoclass:: config
.. autoclass:: NetworkXConfig
.. autoclass:: Config
