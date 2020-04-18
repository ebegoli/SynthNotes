import os
import shutil
import subprocess
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def test_preprocess_execution():
    testdir = os.path.dirname(__file__)
    # clear out anything leftover from previous tests
    if os.path.isdir(testdir+'/preprocessed'):
        shutil.rmtree(testdir+'/preprocessed')
    cargs = ['synthnotes','preprocess','--pq_files',testdir+'/verify/parsed/','--output',testdir+'/preprocessed/','--mimic_notes',testdir+'/notes/mimic.parquet','--seed','0']
    subprocess.call(cargs)
    results = os.listdir(testdir+"/preprocessed/")
    assert len(results) == 4
    
def test_preprocess_output():
    testdir = os.path.dirname(__file__)

    test_mentions = pq.read_table(f'{testdir}/preprocessed/mentions.parquet').to_pandas()
    verify_mentions = pq.read_table(f'{testdir}/verify/preprocessed/mentions.parquet').to_pandas()
    test_mentions.drop(['id','sent_id'],axis=1, inplace=True)
    verify_mentions.drop(['id','sent_id'],axis=1, inplace=True)
    assert test_mentions.equals(verify_mentions)

    test_templates = pq.read_table(f'{testdir}/preprocessed/templates.parquet').to_pandas()
    verify_templates = pq.read_table(f'{testdir}/verify/preprocessed/templates.parquet').to_pandas()
    test_templates.drop(['sent_id'],axis=1, inplace=True)
    verify_templates.drop(['sent_id'],axis=1, inplace=True)
    assert test_templates.equals(verify_templates)

    test_sentences = pq.read_table(f'{testdir}/preprocessed/sentences.parquet').to_pandas()
    verify_sentences = pq.read_table(f'{testdir}/verify/preprocessed/sentences.parquet').to_pandas()
    test_sentences.drop(['sent_id'],axis=1, inplace=True)
    verify_sentences.drop(['sent_id'],axis=1, inplace=True)
    assert test_sentences.equals(verify_sentences)

    test_umls = pq.read_table(f'{testdir}/preprocessed/umls.parquet').to_pandas()
    verify_umls = pq.read_table(f'{testdir}/verify/preprocessed/umls.parquet').to_pandas()
    test_umls.drop(['id'],axis=1, inplace=True)
    verify_umls.drop(['id'],axis=1, inplace=True)
    assert test_umls.equals(verify_umls)

    #for dirname in dirs:
        # check that the contents are actually right

#exit()
#        dirhash = subprocess.check_output(["sha1sum",dirname+"/* | sha1sum"])
#        verifyhash = subprocess.check_output(["sha1sum", testdir+"/"+os.path.relpath(dirname,testdir+"/parsed")+"/* | sha1sum"])
#        assert dirhash == verifyhash
