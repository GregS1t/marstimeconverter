Examples
========

Visualizing LMST over time:

.. code-block:: python

   from marstimeconverter.plotting import plot_lmst_vs_utc
   from marstimeconverter.converter import MarsTimeConverter

   mtc = MarsTimeConverter(mission="Curiosity")
   plot_lmst_vs_utc(mtc, "2022-01-01", num_days=5)
