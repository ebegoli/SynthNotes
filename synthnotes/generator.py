from pkg_resources import resource_filename

from string import Template
import json

from synthnotes.properties import SubsManager


class Generator(object):

    def __init__(self,
                 base_file=resource_filename(__name__, 'resources/test.template'),
                 subs_file=resource_filename(__name__, 'resources/subs.json'),
                 ):
        # read the files, the subs file is read using json method
        with open(base_file, 'r') as fh:
            self.base = fh.read()
        with open(subs_file, 'r') as fh:
            self.subs = json.load(fh)

        # TODO: Error and format checking on input base
        # create a template from the base
        self.t = Template(self.base)
        self.sm = SubsManager(self.subs)

    def generate(self):
        # create a dictionary for subs by randomly selecting values from the list
        # d = {k: random.choice(v) for k, v in self.subs.items()}
        return self.t.safe_substitute(self.sm.mappings)
