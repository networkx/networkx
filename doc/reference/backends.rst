********
Backends
********

NetworkX can be configured to use separate thrid-party backends to improve
performance and add functionality. Backends are optional, installed separately,
and can be enabled either directly in the user's code or through environment
variables.

.. note:: The interface used by developers creating custom NetworkX backends is
   receiving frequent updates and improvements. Participating in weekly
   `NetworkX dispatch meetings
   <https://scientific-python.org/calendars/networkx.ics>`_ is an excellent way
   to stay updated and contribute to the ongoing discussions.

.. automodule:: networkx.utils.backends

.. autosummary::
   :toctree: generated/

   _dispatchable
