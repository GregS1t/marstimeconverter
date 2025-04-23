Usage
=====

To get started with MarsTimeConverter:

.. code-block:: python

   from marstimeconverter.converter import MarsTimeConverter

   mtc = MarsTimeConverter(mission="InSight")
   utc_date = "2022-08-10T12:00:00Z"
   lmst = mtc.utc2lmst(utc_date)
   print(f"LMST: {lmst}")
