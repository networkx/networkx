********************
Backends and Configs
********************

Backends let you execute an alternative backend implementation instead of NetworkX's
pure Python dictionaries implementation. Configs provide library-level storage
of configuration settings that can also come from environment variables.

.. note:: NetworkX backend and configuration systems are receiving frequent updates
   and improvements. The user interface for using backends is generally stable.
   In the unlikely case where compatibility-breaking changes are necessary to the
   backend or config APIs, the standard `deprecation policy <https://networkx.org/documentation/stable/developer/deprecations.html>`_
   of NetworkX may not be followed. This flexibility is intended to allow us to
   respond rapidly to user feedback and improve usability, and care will be taken
   to avoid unnecessary disruption. Developers of NetworkX backends should regularly
   monitor updates to maintain compatibility. Participating in weekly
   `NX-dispatch meetings <https://scientific-python.org/calendars/networkx.ics>`_
   is an excellent way to stay updated and contribute to the ongoing discussions.

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
