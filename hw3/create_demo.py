import argparse
import configparser
from time import sleep
import tensorflow as tf

from env import FlappyEnv
from net import make_conv_net
import numpy as np
import pickle
from pathlib import Path

from util import print_state_with_curses
import curses


def create_demo_from_weights(screen, weights_path, output_file):
    model = make_conv_net()
    model.load_weights(weights_path)
    env = FlappyEnv(use_pipes=True)
    s = env.reset()
    d = False
    states = [s[-1]]
    while not d:
        s = np.array(s).reshape((1, 50, 50, 4))
        actions = model(s, training=False)[0].numpy()
        a = tf.argmax(actions).numpy()
        s, rew, d = env.step(a)
        states.append(s[-1])
    pickle.dump(states, open(output_file, 'wb'))
    try:
        for state in states:
            print_state_with_curses(state, screen)
            sleep(0.1)
    except:
        print('Screen is too small to visualize the episode.',
              'Try making your terminal fullscreen or reducing terminal font size.')
        curses.nocbreak()
        screen.keypad(False)
        curses.echo()
        curses.endwin()
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()
    print(len(states))


def main(args):
    config = configparser.ConfigParser()
    config_filepath = Path.cwd() / 'configs' / args.config
    config.read(config_filepath)
    weights_path = config['files'][args.weights_path]
    output_file = Path.cwd() / config['files']['episode_states_dir'] / args.output_file
    screen = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    create_demo_from_weights(screen, weights_path, output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='pipes', help='Configuration file to use')
    parser.add_argument('-w', '--weights_path', default='best_weights_path',
                        help='Path the weights directory. Defaults to the "best" performing weights seen')
    parser.add_argument('-o', '--output_file', default='new_demo.p', help='Name of output file')
    pargs = parser.parse_args()
    main(pargs)


