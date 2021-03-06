import itertools
import os

import numpy as np
import pandas as pd

import energy_py
from energy_py import all_combinations
from energy_py.agents import ClassifierCondition as Cond


STRATS = {'strat_1': {'conditions': [Cond(0, 'Very High', '=='),
                                     Cond(6, 'Very High', '!=')],
                      'action': np.array(1),
                      'no_op': np.array(0)},

          'strat_2': {'conditions': [Cond(0, 'High', '=='),
                                     Cond(6, 'Very High', '!='),
                                     Cond(6, 'Very High', '!=')],
                      'action': np.array(1),
                      'no_op': np.array(0)}}


def run_single_classifier_experiment(strageties,
                                     expt_name,
                                     dataset_name,
                                     run_name):

    for strat in strageties:
        agent_config[strat] = STRATS[strat]

    env_config = {'env_id': 'Flex-v1',
                  'dataset_name': dataset_name,
                  'episode_length': 0,
                  'flex_size': 0.02,
                  'max_flex_time': 6,
                  'relax_time': 0}

    expt_path = os.path.join(os.getcwd(),
                             'results',
                             expt_name)

    paths = energy_py.make_paths(expt_path, run_name=run_name)
    logger = energy_py.make_logger(paths, 'master')

    energy_py.experiment(agent_config=agent_config,
                         env_config=env_config,
                         total_steps=total_steps,
                         paths=paths,
                         seed=args.seed)


if __name__ == '__main__':
    args = energy_py.make_expt_parser()
    total_steps = 1e2

    #  this is slightly hacky - need the list of column names from the
    #  original observation to know what the agent added from the env
    obs_info = pd.read_csv(os.path.join(os.getcwd(),
                                        'datasets',
                                        args.dataset_name,
                                        'observation.csv'),
                           index_col=0).columns.tolist()

    agent_config = {'agent_id': 'ClassifierAgent',
                    'total_steps': total_steps,
                    'obs_info': obs_info,
                    'no_op': np.array(0),
                    'stop_action': np.array(2)
                    }

    #  TODO should look at the keys of STRATS
    all_strategies = all_combinations('strat_1', 'strat_2')

    for i, strats in enumerate(all_strategies):
        run_single_classifier_experiment(strats,
                                         expt_name=args.expt_name,
                                         dataset_name=args.dataset_name,
                                         run_name='all_strat_{}'.format(i))
