********************
Backends and Configs
********************

Backends let you execute an alternative backend implementation instead of NetworkX's
pure Python dictionaries implementation. Configs provides library level storage
of configuration settings that otherwise might come from environment variables.

.. note:: Both NetworkX backend and config systems are new and and actively developed,
   with frequent updates and improvements. While the backend user interface is unlikely
   to make breaking changes, the backend developers may see some need to update
   their code (within a deprecation period). The NetworkX backend developers should
   regularly monitor the new updates to maintain compatibility. Participating in weekly
   `NX-dispatch meetings <https://scientific-python.org/calendars/networkx.ics>`_
   is an excellent way to stay updated and to contribute to the ongoing discussions.

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
