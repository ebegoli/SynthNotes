#!/usr/bin/env python
"""
    Script to generate sythetic pyschiatric notes.
    The base file contains the basic format of the notes with random value
    place holder names having a dollar sign in front of them.
    The subs file is a json file whose keys are the place holder names and
    values are a list of possible values that can be taken.
"""
import random
import json
import argparse
from tqdm import trange
from os import path
from string import Template

from subsmanager import SubsManager


def main(base_file, subs_file, n_notes=1, prefix='', ext='note', outdir='./'):

    # read the files, the subs file is read using json method
    with open(base_file, 'r') as fh:
        base = fh.read()
    with open(subs_file, 'r') as fh:
        subs = json.load(fh)

    # TODO: Error and format checking on input base
    # create a template from the base
    sm = SubsManager(subs)

    t = Template(base)

    print("Generating {} synthetic notes".format(n_notes))
    for i in trange(n_notes):
        # create a dictionary for subs by randomly selecting values from the list
        # d = {k: random.choice(v) for k, v in subs.items()}

        note = t.safe_substitute(sm.mappings)
        out_file = prefix + str(i+1) + '.' + ext
        out_path = path.join(outdir, out_file)

        with open(out_path, 'w') as fh:
            fh.write(note)
    # print(note)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-bf', '--baseFile', help='Base file with format', required=True)
    parser.add_argument('-sf', '--subsFile', help='JSON file with substitutes', required=True)
    parser.add_argument('-n', '--number', help='Number of notes required (default is 1)', default=1)
    parser.add_argument('-p', '--prefix', help='Prefix before number (default is note_)', default='note_')
    parser.add_argument('-e', '--ext', help='Extension of file (default is note)', default='note')
    parser.add_argument('-o', '--outdir', help='Directory to write output files to', default='./')
    args = parser.parse_args()
    main(args.baseFile, args.subsFile, int(args.number), args.prefix, args.ext, args.outdir)
