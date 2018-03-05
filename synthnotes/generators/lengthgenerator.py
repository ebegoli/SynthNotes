from pkg_resources import resource_filename

import pandas as pd
import numpy as np


class LengthGenerator(object):
    def __init__(self,
                 length_file=resource_filename('synthnotes.resources',
                                               'note_lengths.csv')):
        # print(length_file)
        df = pd.read_csv(length_file)
        notes_count = df['count'].sum()
        df['probability'] = df['count'] / notes_count
        self.note_lengths = df['note_length'].as_matrix()
        self.p = df['probability'].as_matrix()

    def generate(self, size=1):
        return np.random.choice(self.note_lengths,
                                size=size,
                                p=self.p)
