********************
Backends and Configs
********************

.. note:: Both NetworkX backend and config systems are experimental.

   Backends let you execute an alternative backend implementation instead of NetworkX's
   pure Python dictionaries implementation. The config system provides library level
   storage of configuration settings that otherwise might come from environment
   variables.

   Both systems are new and under active development. Hence, they will be regularly
   updated with new features and improvements. At this stage, there are no deprecation
   warnings for these systems. This may change as the features mature and become more
   stable.

   Users of these systems should expect minimal need for code updates to
   maintain compatibility. However, staying informed about new features and changes
   will be beneficial. Developers working on these systems should monitor changes
   closely. Participating in weekly NX-dispatch meetings is an excellent way to stay
   updated and contribute to discussions about ongoing developments.
   
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
