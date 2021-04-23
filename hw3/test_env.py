import argparse
import curses
from time import sleep
from env import FlappyEnv
from util import print_state_with_curses
import pickle

def test_environment(use_pipes=False, sleep_time=0.15):
    screen = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    if not use_pipes:
        env = FlappyEnv(use_pipes=False)
    else:
        env = FlappyEnv(use_pipes=True, deterministic=True)
    s = env.reset()
    states = [s[-1]]
    all_actions = [0]
    for _ in range(20):
        all_actions += [1, 0, 0, 0, 0, 0]

    for action in all_actions:
        s, rew, d = env.step(action)
        states.append(s[-1])
        if d:
            break
    try:
        for state in states:
            print_state_with_curses(state, screen)
            sleep(sleep_time)
    except:
        print('Your terminal screen is too small to visualize the episode. Try maximizing your screen or adjusting '
              'your terminal fonts.')
    pickle.dump(states, open('test.p', 'wb'))
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()


def main(args):
    test_environment(args.use_pipes, args.speed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--use_pipes', action='store_true',
                        help='Determines whether the environment to test uses the pipe')

    parser.add_argument('-s', '--speed', type=float, default=0.1,
                        help='Sleep time between frames. Lower is faster')
    pargs = parser.parse_args()
    main(pargs)

