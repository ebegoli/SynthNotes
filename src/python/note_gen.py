#!/usr/bin/env python

import random
import json
import argparse

from string import Template

def main(base_file, subs_file, n_notes):
    print("Reading from {} file".format(base_file))
    with open(base_file, 'r') as fh:
        base = fh.read()

    print("Reading from {} file".format(subs_file))
    with open(subs_file, 'r') as fh:
        subs = json.load(fh)

    t = Template(base)
    d = {k: random.choice(v) for k, v in subs.items()}

    print("Generating {} synthetic notes".format(n_notes))
    note = t.safe_substitute(d).strip()
    print(note)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-bf', '--baseFile', help='Base file with format', required=True)
    parser.add_argument('-sf', '--subsFile', help='JSON file with substitutes', required=True)
    parser.add_argument('-n', '--number', help='Number of notes required (default 10)', default=10)
    args = parser.parse_args()
    main(args.baseFile, args.subsFile, args.number)
    # main()
