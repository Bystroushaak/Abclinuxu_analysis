Abclinuxu analysis and archival scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Hail `/r/datahoarder <https://www.reddit.com/r/DataHoarder/>`_.


download_blogtree.py
--------------------

Download full archive of the abclinuxu blogs. Format is serialized objects in sqlitedb.


convert_blogtree_to_clean_sqlite.py
-----------------------------------

If you don't like object serialization, use this script to convert *blogtree* to clean sqlite format.


blog_analysis.py
----------------

Analysis of blogs. Output is graphs and .csv files with various tracked parameters.


generate_gephi_interaction_dataset.py
-------------------------------------

Generate `Gephi <https://gephi.org/>`_ import sqlite file showing who talks with who in comments.


generate_cal_data.py
--------------------

Generate calendar data files for `termgraph tool <https://github.com/mkaz/termgraph>`_.
