import os
import shutil
import subprocess
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def test_parse_execution():
    testdir = os.path.dirname(__file__)
    #If we don't remove leftovers, running parse will just vomit file copies and create a second copy of the dataframe.
    if os.path.isdir(testdir+'/parsed'):
        shutil.rmtree(testdir+'/parsed')
    cargs = ['synthnotes','parse','--xml-dir',testdir+'/xml/','--output',testdir+'/parsed/','--seed','0']
    subprocess.call(cargs)
    dirs = os.listdir(testdir+"/parsed/")
    assert len(dirs) == 5
    
def test_parse_output():
    testdir = os.path.dirname(__file__)

    test_mentions = pq.read_table(f'{testdir}/parsed/mentions').to_pandas()
    verify_mentions = pq.read_table(f'{testdir}/verify/parsed/mentions').to_pandas()
    test_mentions.drop(['id','sent_id'],axis=1, inplace=True)
    verify_mentions.drop(['id','sent_id'],axis=1, inplace=True)
    assert test_mentions.equals(verify_mentions)

    test_predicates = pq.read_table(f'{testdir}/parsed/predicates').to_pandas()
    verify_predicates = pq.read_table(f'{testdir}/verify/parsed/predicates').to_pandas()
    test_predicates.drop(['id','sent_id'],axis=1, inplace=True)
    verify_predicates.drop(['id','sent_id'],axis=1, inplace=True)
    assert test_predicates.equals(verify_predicates)

    test_sentences = pq.read_table(f'{testdir}/parsed/sentences').to_pandas()
    verify_sentences = pq.read_table(f'{testdir}/verify/parsed/sentences').to_pandas()
    test_sentences.drop(['id'],axis=1, inplace=True)
    verify_sentences.drop(['id'],axis=1, inplace=True)
    assert test_sentences.equals(verify_sentences)

    test_tokens = pq.read_table(f'{testdir}/parsed/tokens').to_pandas()
    verify_tokens = pq.read_table(f'{testdir}/verify/parsed/tokens').to_pandas()
    test_tokens.drop(['id','sent_id'],axis=1, inplace=True)
    verify_tokens.drop(['id','sent_id'],axis=1, inplace=True)
    assert test_tokens.equals(verify_tokens)

    test_umls = pq.read_table(f'{testdir}/parsed/umls_concepts').to_pandas()
    verify_umls = pq.read_table(f'{testdir}/verify/parsed/umls_concepts').to_pandas()
    test_umls.drop(['id'],axis=1, inplace=True)
    verify_umls.drop(['id'],axis=1, inplace=True)
    assert test_umls.equals(verify_umls)

    #for dirname in dirs:
        # check that the contents are actually right

#exit()
#        dirhash = subprocess.check_output(["sha1sum",dirname+"/* | sha1sum"])
#        verifyhash = subprocess.check_output(["sha1sum", testdir+"/"+os.path.relpath(dirname,testdir+"/parsed")+"/* | sha1sum"])
#        assert dirhash == verifyhash
