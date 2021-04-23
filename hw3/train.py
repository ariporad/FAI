import argparse
import configparser
import pandas as pd
from dqn import dqn
from net import make_conv_net
from pathlib import Path


def main(args):
    config = configparser.ConfigParser()
    config_filepath = Path.cwd() / 'configs' / args.config
    config.read(config_filepath)
    model = make_conv_net()
    model_target = make_conv_net()
    if args.load_backup:
        model.load_weights(config['files']['backup_weights_path'])
        model_target.load_weights(config['files']['backup_weights_path'])
        df = pd.read_csv(config['files']['log_path'])
        s = df.to_dict('series')
        log = {'avg_reward': s['avg_reward'].values.tolist(),
               'best_reward': s['best'].values.tolist(),
               'episode': s['episode'].values.tolist(),
               'q_vals': s['q_vals'].values.tolist(),
               'avg_steps': s['avg_steps'].values.tolist(),
               'best_steps': s['best_steps'].values.tolist()}
        start_episode = log['episode'][-1] + 10
    else:
        log = {'avg_reward': [],
               'best_reward': [],
               'episode': [],
               'q_vals': [],
               'avg_steps': [],
               'best_steps': []}
        start_episode = 0
    dqn(start_episode, model, model_target, log, config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='flight', help='Configuration file to use')
    parser.add_argument('-l', '--load_backup', action='store_true', help='Load existing backup weights')
    pargs = parser.parse_args()
    main(pargs)

