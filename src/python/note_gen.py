#!/usr/bin/env python

import random
import json

from string import Template

def main():
    with open('test.base', 'r') as base_file:
        base = base_file.read()

    with open('values.json', 'r') as value_file:
        values = json.load(value_file)

    t = Template(base)
    d = {k: random.choice(v) for k, v in values.items()}

    note = t.safe_substitute(d)
    print(note)

if __name__=='__main__':
    main()
