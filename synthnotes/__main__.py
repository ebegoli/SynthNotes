import click
import os
import pandas as pd

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
@click.option('--xml-dir', default='data/xml_files', help='File path to directory of xml files')
@click.option('--output', default='data/xml_extracted', help='File path to storage extracted xml data parquet files')
@click.option('--fs', default='local', type=click.Choice(['local', 'hdfs']), help='Use local or hdfs storage' )
def parse(xml_dir, output, fs):
    parser = CtakesXmlParser()
    files = get_files(fs, xml_dir)
    parsed = []
    for f in files:
        xml_result = parser.parse(f)
        parsed.append(xml_result)

    for p in parsed:
        for key, val in p.items():
            feature_df = pd.DataFrame(list(val))  
            if feature_df.shape[0] > 0:
                table = pa.Table.from_pandas(feature_df)                
                pq.write_to_dataset(table, output + f'/{key}',
                                    filesystem=None)


@cli.command()
@click.option('--pq_files', default='data/xml_extracted', help='File path to directory of extracted xml data parquet files')
@click.option('--output', default='data/processed_dfs', help='File path to storage for preprocessed dataframes to be stored for clustering.  This directory should exist.')
@click.option('--mimic_notes', default='data/note-events.parquet', help='File path to mimic notes in parquet file')
def preprocess(pq_files, output, mimic_notes):
    p = Preprocessor(pq_files, output, mimic_notes)
    p.preprocess()

@cli.command()
@click.option('--pq_files', default='data/processed_dfs', help='File path to processed xml data parquet files')
@click.option('--output', default='data/clustering', help='File path to storage for clustering data')
def cluster(pq_files, output):
    clusterer = Clusterer(pq_files, output)
    clusterer.cluster()

@cli.command()
@click.option('-n', default=1, help='Number of notes to generate')
@click.option('--pq_files', default='data/clustering', help='File path to clustering data')
@click.option('--output', default='data/generated_notes', help='File path to output generated notes')
def generate(n, pq_files, output):
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