#!/usr/bin/env python
"""
    Script to generate sythetic pyschiatric notes.
    The base file contains the basic format of the notes with random value
    place holder names having a dollar sign in front of them.
    The subs file is a json file whose keys are the place holder names and
    values are a list of possible values that can be taken.
"""
import json
import argparse
from tqdm import trange
import os
from string import Template

from synthnotes.properties import SubsManager


def main(template, mappings, n_notes=1, prefix='note_', extension='note', output_dir='./'):
    # read the files, the subs file is read using json method
    with open(template, 'r') as fh:
        base = fh.read()
    with open(mappings, 'r') as fh:
        subs = json.load(fh)

    # TODO: Error and format checking on input base
    # create a template from the base
    sm = SubsManager(subs)

    t = Template(base)

    print("Generating {} synthetic notes".format(n_notes))
    for i in trange(n_notes):
        note = t.safe_substitute(sm.mappings)
        # a total hack. some substitution values may also contain variables
        # that need to be replaced.  This is the easiest thing to do for now
        t2 = Template(note)
        note = t2.safe_substitute(sm.mappings)
        out_file = prefix + str(i + 1) + '.' + extension
        out_path = os.path.join(output_dir, out_file)
        os.makedirs(os.path.dirname(out_path, ), exist_ok=True)

        with open(out_path, 'w') as fh:
            fh.write(note)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    help_str = """
        Path to json config file. Required fields: template, mappings
    """
    parser.add_argument('-c', '--config', help=help_str,
                        default="synthnotes/resources/conf.json",
                        required=False)
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        conf = json.load(f)

    # Compute absolute path of config files

    path_prefix = os.path.dirname(os.path.abspath(args.config))
    print(path_prefix)
    conf['mappings'] = os.path.join(path_prefix, conf['mappings'])
    conf['template'] = os.path.join(path_prefix, conf['template'])
    conf['output_dir'] = os.path.join(path_prefix, conf['output_dir'])
    main(**conf)
