from ..config import *
from .record import *

import pandas as pd
import numpy as np
import os

__all__ = ['load_note_df']

DROPPED_COLUMNS = ['#', 'separator', 'continuous']
RENAMED_COLUMNS = ['bar', 'bpm', 'time_unit', 'timestamp', 'label']
NOTE_MAGIC_STR = 'taiko_song_%d_%s_info.csv'


class _Note(object):

    def __init__(self, who_id, song_id, order_id):
        self._drummer_df = load_drummer_df()
        self._who_id = who_id
        self._song_id = song_id
        self._order_id = order_id

        difficulty = get_record(who_id, song_id, order_id)['difficulty']
        note_file_name = NOTE_MAGIC_STR % (self._song_id, difficulty)

        self._note_df = pd.read_csv(os.path.join(TABLE_PATH, note_file_name))
        self._note_df.drop(DROPPED_COLUMNS, axis=1, inplace=True)
        self._note_df.columns = RENAMED_COLUMNS
        self._note_df['label'] = self._note_df['label'].apply(transform_hit_type_label)

    @property
    def note_df(self):
        return self._note_df


def transform_hit_type_label(label):
    if label in [1, 2, 3, 4]:
        return 1
    elif label in [5, 6]:
        return 2
    return 0


def load_note_df(who_id, song_id, order_id):
    return _Note(who_id, song_id, order_id).note_df