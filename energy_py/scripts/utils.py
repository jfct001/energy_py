"""
A collection of helper functions.
"""

import configparser
import csv
from itertools import combinations
import logging
import pickle
import os

import pandas as pd
import tensorflow as tf


logger = logging.getLogger(__name__)


def all_combinations(*args):
    """
    Creates all combinations of an iterable of arguments

    args
        any iterable sequence

    returns
        combinations (list)
    """
    combos = []
    #  to get all combinations of any size we iterate over the range of
    #  lengths for each combination
    for length in range(1, len(args)+1):

        #  create all combinations of a given length
        for combo in combinations(args, length):
            combos.append(combo)

    return combos


def ensure_dir(file_path):
    """
    Checks a directory exists.  If it doesn't - makes it.

    args
        file_path (str)
    """
    directory = os.path.dirname(file_path)

    if not os.path.exists(directory):
        os.makedirs(directory)


def load_csv(*paths):
    """
    Loads a csv into a dataframe

    args
        paths (iterable) strings to be formed into a path
    """
    path = os.path.join(*paths)
    return pd.read_csv(path,
                     index_col=0,
                     parse_dates=True)


def parse_ini(filepath, section):
    """
    Reads a single ini file

    args
        filepath (str) location of the .ini
        section (str) section of the ini to read

    returns
        config_dict (dict)

    Also converts boolean arguments from str to bool
    """
    logger.info('reading {}'.format(filepath))
    config = configparser.ConfigParser()
    config.read(filepath)

    #  check to convert boolean strings to real booleans
    config_dict = dict(config[section])

    for k, val in config_dict.items():
        if val == 'True':
            config_dict[k] = True

        if val == 'False':
            config_dict[k] = False

    return config_dict


def dump_pickle(obj, name):
    """
    Saves an object to a pickle file.

    args
        obj (object)
        name (str) path of the dumped file
    """
    with open(name, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(name):
    """
    Loads a an object from a pickle file.

    args
        name (str) path to file to be loaded

    returns
        obj (object)
    """
    with open(name, 'rb') as handle:
        return pickle.load(handle)


def make_logger(paths, name=None):
    """
    Sets up the energy_py logging stragety.  INFO to console, DEBUG to file.

    args
        paths (dict)
        name (str) optional logger name

    returns
        logger (object)
    """
    if name:
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger(__name__)

    fmt = '%(asctime)s [%(levelname)s]%(name)s: %(message)s'

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {'standard': {'format': fmt,
                                    'datefmt': '%Y-%m-%d %H:%M:%S'}},

        'handlers': {'console': {'level': 'INFO',
                                 'class': 'logging.StreamHandler',
                                 'formatter': 'standard'},

                     'debug_file': {'class': 'logging.FileHandler',
                                    'level': 'DEBUG',
                                    'filename': paths['debug_log'],
                                    'mode': 'w',
                                    'formatter': 'standard'},

                     'info_file': {'class': 'logging.FileHandler',
                                   'level': 'INFO',
                                   'filename': paths['info_log'],
                                   'mode': 'w',
                                   'formatter': 'standard'}},

        'loggers': {'': {'handlers': ['console', 'debug_file', 'info_file', ],
                         'level': 'DEBUG',
                         'propagate': True}}})

    return logger


def save_args(config, path):
    """
    Saves a config dictionary to a text file

    args
        config (dict)
        path (str) path for output text file

    returns
        writer (object) csv Writer object
    """
    with open(path, 'w') as outfile:
        writer = csv.writer(outfile)

        for k, v in config.items():
            logger.debug('{} : {}'.format(k, v))
            writer.writerow([k]+[v])

    return writer


class TensorboardHepler(object):
    """
    Holds a FileWriter and method for adding summaries

    args
        logdir (path)
    """
    def __init__(self, logdir):
        self.writer = tf.summary.FileWriter(logdir)
        self.steps = 0

    def add_summaries(self, summaries):
        """
        Adds non-tensorflow data to tensorboard.

        args
            summaries (dict)
        """
        self.steps += 1
        for tag, var in summaries.items():
            var = float(var)
            summary = tf.Summary(value=[tf.Summary.Value(tag=tag,
                                                         simple_value=var)])
            self.writer.add_summary(summary, self.steps)

        self.writer.flush()
