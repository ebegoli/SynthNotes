import os
import shutil
import subprocess
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def test_cluster_execution():
    testdir = os.path.dirname(__file__)
    # clear out anything leftover from previous tests
    if os.path.isdir(testdir+'/cluster'):
        shutil.rmtree(testdir+'/cluster')
    cargs = ['synthnotes','cluster','--pq_files',testdir+'/verify/preprocessed/','--output',testdir+'/cluster/','--seed','0']
    subprocess.call(cargs)
    results = os.listdir(testdir+"/cluster/")
    assert len(results) == 5

def test_cluster_output():
    testdir = os.path.dirname(__file__)

    test_clustering = pq.read_table(f'{testdir}/cluster/cluster_by_pos.parquet').to_pandas()
    verify_clustering = pq.read_table(f'{testdir}/verify/cluster/cluster_by_pos.parquet').to_pandas()
    assert test_clustering.equals(verify_clustering)

    test_mentions = pq.read_table(f'{testdir}/cluster/mentions.parquet').to_pandas()
    verify_mentions = pq.read_table(f'{testdir}/verify/cluster/mentions.parquet').to_pandas()
    test_mentions.drop(['id','sent_id'],axis=1, inplace=True)
    verify_mentions.drop(['id','sent_id'],axis=1, inplace=True)
    assert test_mentions.equals(verify_mentions)

    test_templates = pq.read_table(f'{testdir}/cluster/templates.parquet').to_pandas()
    verify_templates = pq.read_table(f'{testdir}/verify/cluster/templates.parquet').to_pandas()
    test_templates.drop(['sent_id'],axis=1, inplace=True)
    verify_templates.drop(['sent_id'],axis=1, inplace=True)
    assert test_templates.equals(verify_templates)

    test_sentences = pq.read_table(f'{testdir}/cluster/sentences.parquet').to_pandas()
    verify_sentences = pq.read_table(f'{testdir}/verify/cluster/sentences.parquet').to_pandas()
    test_sentences.drop(['sent_id'],axis=1, inplace=True)
    verify_sentences.drop(['sent_id'],axis=1, inplace=True)
    assert test_sentences.equals(verify_sentences)

    test_umls = pq.read_table(f'{testdir}/cluster/umls.parquet').to_pandas()
    verify_umls = pq.read_table(f'{testdir}/verify/cluster/umls.parquet').to_pandas()
    test_umls.drop(['id'],axis=1, inplace=True)
    verify_umls.drop(['id'],axis=1, inplace=True)
    assert test_umls.equals(verify_umls)

    #for dirname in dirs:
        # check that the contents are actually right

#exit()
#        dirhash = subprocess.check_output(["sha1sum",dirname+"/* | sha1sum"])
#        verifyhash = subprocess.check_output(["sha1sum", testdir+"/"+os.path.relpath(dirname,testdir+"/parsed")+"/* | sha1sum"])
#        assert dirhash == verifyhash
