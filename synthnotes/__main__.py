import click
import os
import pandas as pd
import random
import numpy.random as npr

from synthnotes.xml_processing import CtakesXmlParser
from synthnotes.preprocessor import Preprocessor
from synthnotes.clustering import Clusterer
from synthnotes.generator import Generator

import pyarrow as pa
import pyarrow.parquet as pq

@click.group()
def cli():
    pass

@cli.command()
@click.option('--xml-dir', default='data/xml_files', help='File path to directory of xml files. This directory must have NOTHING else in it.')
@click.option('--output', default='data/xml_extracted', help='File path to stoge extracted xml data parquet files')
@click.option('--fs', default='local', type=click.Choice(['local', 'hdfs']), help='Use local or hdfs storage' )
@click.option('--seed',default=None,help='Optional; specify random seed.')
def parse(xml_dir, output, fs, seed):
    xml_dir = xml_dir.rstrip('/') # remove trailing /
    output = output.rstrip('/')
    os.makedirs(output,exist_ok=True) # create output directory if it does not exist
    if seed is not None:
        random.seed(int(seed))
        npr.seed(int(seed))

    parser = CtakesXmlParser()
    files = get_files(fs, xml_dir)
    parsed = []
    for f in files:
        xml_result = parser.parse(f)
        parsed.append(xml_result)

    def filenamer(x):
        print(x)
        try:
            return '-'.join(x)+'.parquet'
        except TypeError:
            return str(x)+'.parquet'

    for p in parsed:
        for key, val in p.items():
            feature_df = pd.DataFrame(list(val))
            if feature_df.shape[0] > 0:
                table = pa.Table.from_pandas(feature_df)
                #pq.write_to_dataset(table, output + f'/{key}', partition_filename_cb=filenamer,
                #pq.write_to_dataset(table, output + f'/{key}', partition_filename_cb=lambda x:'-'.join(x)+'.parquet',
                pq.write_to_dataset(table, output + f'/{key}',
                                    filesystem=None)


@cli.command()
@click.option('--pq_files', default='data/xml_extracted', help='File path to directory of extracted xml data parquet files')
@click.option('--output', default='data/processed_dfs', help='File path to storage directory for preprocessed dataframes to be stored for clustering.')
@click.option('--mimic_notes', default='data/note-events.parquet', help='File path to mimic notes in parquet file')
@click.option('--seed',default=None,help='Optional; specify random seed.')
def preprocess(pq_files, output, mimic_notes, seed):
    pq_files = pq_files.rstrip('/') # remove trailing /
    output = output.rstrip('/')
    os.makedirs(output,exist_ok=True) # create output directory if it does not exist
    if seed is not None:
        random.seed(int(seed))
        npr.seed(int(seed))
    p = Preprocessor(pq_files, output, mimic_notes)
    p.preprocess()

@cli.command()
@click.option('--pq_files', default='data/processed_dfs', help='File path to directory of processed xml data parquet files')
@click.option('--output', default='data/clustering', help='File path to directory for storage for clustering data')
@click.option('--n_clusters',default='120',help='Optional; specify number of clusters')
@click.option('--seed',default=None,help='Optional; specify random seed.')
def cluster(pq_files, output, n_clusters, seed):
    pq_files = pq_files.rstrip('/') # remove trailing /
    output = output.rstrip('/')
    os.makedirs(output,exist_ok=True) # create output directory if it does not exist
    num_clusters = int(n_clusters)
    if seed is not None:
        random.seed(int(seed))
        npr.seed(int(seed))
    clusterer = Clusterer(pq_files, output, num_clusters)
    clusterer.cluster()

@cli.command()
@click.option('-n', default=1, help='Number of notes to generate')
@click.option('--pq_files', default='data/clustering', help='File path to directory of clustering data')
@click.option('--output', default='data/generated_notes', help='File path to directory in which to output generated notes')
@click.option('--seed',default=None,help='Optional; specify random seed.')
def generate(n, pq_files, output, seed):
    pq_files = pq_files.rstrip('/') # remove trailing /
    output = output.rstrip('/')
    os.makedirs(output,exist_ok=True) # create output directory if it does not exist
    if seed is not None:
        random.seed(int(seed))
        npr.seed(int(seed))
    gen = Generator(pq_files, output)
    gen.generate(n_notes=n)


def get_files(fs, dirpath):
    abs_path = os.path.abspath(dirpath)
    result = []
    if fs == 'local':
        files = os.listdir(abs_path)
    for f in files:
        result.append(os.path.join(abs_path, f) )

    return result


if __name__ == '__main__':
    cli()
