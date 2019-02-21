from .tools.config import *
from .image import read_result_board_info

from glob import glob
from typing import List
from sklearn import preprocessing
from imblearn.over_sampling import SMOTE
import pandas as pd
import numpy as np
import re
import sys
import posixpath

__all__ = ['load_record_df',
           'get_all_drummers',
           'create_play_result',
           'transform_hit_type',
           'transform_drum_note_hit_type',
           'scale_performance_df']

"""
Constants
"""

SONGS = 4

"""
Modules
"""


def load_record_df(**kwargs) -> pd.DataFrame:
    record_files = glob(posixpath.join(HOME_PATH, '*', '*', 'record_table.csv'))
    record_dfs = []
    for record_file_path in sorted(record_files):
        record_df = pd.read_csv(record_file_path)
        record_dfs.append(record_df)
    record_df = pd.concat(record_dfs, ignore_index=True)

    for key, value in kwargs.items():
        record_df = record_df[record_df[key] == value]

    return record_df


def get_all_drummers() -> List[str]:
    record_df = load_record_df()
    drummers = list(record_df['drummer_name'].unique())

    return drummers


def create_play_result(verbose=1) -> None:
    record_df = load_record_df()

    # only 4 songs we considered
    record_df = record_df[(record_df['song_id'] >= 1) & (record_df['song_id'] <= SONGS)]

    aggregate_dict = {}
    columns = ['id', 'drummer_name', 'song_id', 'p_order', 'capture_datetime'] + RESULT_BOARD_INFO_COLUMNS
    data = {}
    for col in columns:
        data[col] = []

    for id_, row in record_df.iterrows():
        try:
            capture_dir = row['capture_datetime']
            who_name = row['drummer_name']
            song_id = row['song_id']
            dirs = glob(posixpath.join(HOME_PATH, who_name, '*', 'bb_capture', capture_dir))
            capture_dir_path = dirs[0]
            result = read_result_board_info(capture_dir_path)

            # increment p_order
            try:
                aggregate_dict[(who_name, song_id)]
            except KeyError:
                aggregate_dict[(who_name, song_id)] = 0

            p_order = aggregate_dict[(who_name, song_id)] + 1
            aggregate_dict[(who_name, song_id)] = p_order

            data['id'].append(id_)
            data['drummer_name'].append(who_name)
            data['song_id'].append(song_id)
            data['p_order'].append(p_order)
            data['capture_datetime'].append(capture_dir)

            for col in result.keys():
                data[col].append(result[col])

            if verbose > 0:
                message = 'who_name = %s, song_id = %d, p_order = %d, %s\n' \
                          'result = %s\n\n' % \
                          (who_name, song_id, p_order, capture_dir, str(result))
                sys.stdout.write(message)
                sys.stdout.flush()

        except Exception as e:
            print(e)

    play_result_df = pd.DataFrame(data=data)
    play_result_df.to_csv(PLAY_RESULT_TABLE_PATH, index=False, float_format='%.4f')


def transform_hit_type(label) -> int:
    if label in [1, 2]:
        return 1
    if label in [3, 4]:
        return 2
    if label in [5]:
        return 3
    if label in [6]:
        return 4
    if label in [7]:
        return 5

    return 0


def transform_drum_note_hit_type(label) -> int:
    if label in [5, 6, 7]:
        return 5

    return label


def scale_performance_df(df):
    """
    Scale values of required features.

    :return: nothing
    """

    scaler = preprocessing.StandardScaler()
    columns = df.columns
    columns = [col for col in columns if not re.match(NO_SCALE_REGEX, col)]

    subset = df[columns]
    train_x = [tuple(x) for x in subset.values]
    train_x = scaler.fit_transform(train_x)
    new_df = pd.DataFrame(data=train_x, columns=columns)
    df.update(new_df)

    return df


def oversample_performance_df(df):
    x_columns, y_columns = [], []
    for col in df.columns:
        if re.match('hit_type', col):
            y_columns.append(col)
        else:
            x_columns.append(col)

    x = df.drop(y_columns, axis=1)
    y = df[y_columns]
    y = np.ravel(y)

    x_resampled, y_resampled = SMOTE(k_neighbors=3, random_state=0).fit_sample(x, y)

    x_df = pd.DataFrame(columns=x_columns, data=x_resampled)
    y_df = pd.DataFrame(columns=y_columns, data=y_resampled)

    new_df = pd.concat([x_df, y_df], axis=1)
    new_df = new_df[df.columns]

    return new_df