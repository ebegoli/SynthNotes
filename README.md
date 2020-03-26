# Overview
This is the repository for the second version of SynthNotes, a clinical note generation tool for researchers seeking to make their own datasets for studying natural language processing.  This is currently an alpha release; a prototype for development and proof of concept. 

There are two options for installation and running: either locally only, or distributed.  Regardless, note generation happens locally and for the time being will be constrained by your local machine's RAM.  For now, it is suggested to install locally and not rely on the distributed tools like HDFS and RabbitMQ. 

# Installation

Clone the repository:
```
$ git clone https://github.com/ebegoli/SynthNotes.git
```

## Python Environment
SynthNotes uses Python 3.6.  Make sure you have a compatible version of Python installed.  It is also recommended to use some kind of virtual environment tool such as virtualenv or anaconda.  

```
$ pip install -e .
```

## Data Files
SynthNotes version 2 is built off of clinical notes in the Mimic-III database.  In order to run SynthNotes, you will need to get a license for Mimic and install it somewhere locally.  To get access to mimic data see you may find the steps for that process [here](https://mimic.physionet.org/gettingstarted/access/). It isn't necessary to build the entire Postgres database, but you at least need the `note events` table.  It is enough to just download that csv file.  For running cTAKES you will need to extract out the note text which is easily done using pandas [[1]](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html).  For preprocessing, the software expects a parquet file.  Again, this can easily be done with pandas by first reading the csv file and then writing it out using parquet[[2]](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_parquet.html). The supplemental script `csv_to_parquet.py` can perform this task as well.

Parsing also needs to know where the cTAKES output xml files are.  This filepath is passed as a command line argument.  See the help page for information on those variables. Note that the directory containing the cTAKES output must contain ONLY these xml files.

```
$ synthnotes parse --help
```

The various scripts can take specific directory targets as arguments, but have default values throughout the entire pipeline. If you place your XML files in data/xml_files/ and the parquet file in data/note-events.parquet, you can run the pipeline with no filepath arguments. If you do, generated documents will be placed in data/generated_notes/. 


# Running
The pipeline runs as follows;
* parse
* preprocess
* cluster
* generate

Once clustering is complete, generation can be run as many times as desired without rerunning any prior stages. To avoid overwriting previous outputs, it is recommended that you specify different output directories for subsequent runs.

As mentioned above, cTAKES must first be run on the mimic notes data and that output stored in a place where the python program can access it.  That filepath should be passed to the command line arguments. Alternatively, the cTAKES output can be placed in the default input directory data/xml_files/.  You may pass `--help` to the command line program to see more information on those variables.

Once cTAKES has been run and the xml assembled into a single directory, then the parser must be run.  

```
$ synthnotes parse --xml_dir path/to/ctakes/xml/files \
--output path/to/store/extracted/parquet/data \
--fs [local | hdfs]
```

Once the parsing is complete, a set of parquet files containing the extracted xml information will be available in the `--output` directory.  Those parquet files will be used for preprocessing the data for clustering and generation.

To run preprocessing run:
```
$ synthnotes preprocess --pq_files parquet/files/path \
--output path/to/output/dir \
--mimic_notes path/to/mimic-notes/parquet/file
```

To perform clustering run: 

```
$ synthnotes cluster --pq_files path/to/preprocessed/parquet/files \
--output path/to/output/dir
```

`--pq_files` for clustering should be the `--output` from the preprocessing stage.

Finally, note generation can be done with:

```
$ synthnotes generate -n 100 \
--pq_files path/to/clustered/parquet/files \
--output path/to/output/dir
```
It is recommended that you begin by generating a small number of notes, such as 2 or 5, to get a feel for how long this process takes on your machine.
