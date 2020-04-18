import os
import shutil
import subprocess
import filecmp

def test_generate_execution():
    testdir = os.path.dirname(__file__)
    # clear out anything leftover from previous tests
    if os.path.isdir(testdir+'/generate'):
        shutil.rmtree(testdir+'/generate')
    cargs = ['synthnotes','generate','--pq_files',testdir+'/verify/cluster/','--output',testdir+'/generate/','-n','3','--seed','0']
    subprocess.call(cargs)
    results = os.listdir(testdir+"/generate/")
    assert len(results) == 3

def test_generate_output():
    testdir = os.path.dirname(__file__)

    assert filecmp.cmp("generate/note_0.txt","verify/generate/note_0.txt")
    assert filecmp.cmp("generate/note_1.txt","verify/generate/note_1.txt")
    assert filecmp.cmp("generate/note_2.txt","verify/generate/note_2.txt")
