import configparser
from time import sleep
import curses
import pickle
import argparse
from util import print_state_with_curses
from pathlib import Path


def show_demo(states, sleep_time):
    screen = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    for state in states:
        try:
            print_state_with_curses(state, screen)
            sleep(sleep_time)
        except:
            print('Screen is too small to visualize the episode.',
                  'Try making your terminal fullscreen or reducing terminal font size.')
            break
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()


def main(args):
    config = configparser.ConfigParser()
    config_filepath = Path.cwd() / 'configs' / args.config
    config.read(config_filepath)
    states_filepath = Path.cwd() / config['files']['episode_states_dir'] / args.filename
    with open(states_filepath, 'rb') as states_file:
        states = pickle.load(states_file)
        show_demo(states, args.speed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='flight', help='Configuration file to use')
    parser.add_argument('-f', '--filename', default='best.p',
                        help='Filename of episode states file to visualize.')
    parser.add_argument('-s', '--speed', type=float, default=0.1,
                        help='Sleep time between frames. Lower is faster')
    pargs = parser.parse_args()
    main(pargs)



