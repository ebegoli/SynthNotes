from pkg_resources import resource_filename

from string import Template
import json

from synthnotes.properties import SubsManager
from synthnotes.generators import LengthGenerator


class NoteGenerator(object):

    def __init__(self,
                 base_file=resource_filename('synthnotes.resources', 'test.template'),
                 subs_file=resource_filename('synthnotes.resources', 'subs.json'),
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
        self.len_gen = LengthGenerator(resource_filename('synthnotes',
                                                         'resources/notes_lengths.csv'))

    def generate(self):
        rand_len = self.len_gen.generate(size=1)[0]
        note = self.t.safe_substitute(self.sm.mappings)
        return self._adjust_note_len(note, rand_len)

    def _adjust_note_len(self, note, rand_len):

        if rand_len == 0:
            return ''
        note_len = len(note)
        # print(type(note))
        if note_len == rand_len:
            return note
        elif note_len > rand_len:
            return note[:rand_len - 1]
        else:
            n = rand_len // note_len
            rem = rand_len % note_len
            new_note = note * n + note[:rem]
            assert len(new_note) == rand_len
            return new_note
