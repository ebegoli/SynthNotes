# Extra Materials

The files in this directory are not strictly necessary for running SynthNotes, but may be helpful or interesting to users.

## Helper Scripts

The script ``csv_to_parquet.py`` takes a CSV file, such as ``NOTE_EVENTS.csv``, and converts it to a parquet file using the encoding of your choice (default gzip). This may be helpful for converting the MIMIC-III table output to something that can be read by SynthNotes.

## Jupyter Notebooks

These notebooks do not directly interface with the operation of SynthNotes, but may be interesting for users looking for insights into how it functions.

* ``preprocessing.ipynb`` graphically demonstrates how the preprocessing stage works.
* ``clustering.ipynb`` graphically demonstrates how the clustering stage works.
