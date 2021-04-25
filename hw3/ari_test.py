import curses
from util import print_state_with_curses
from env import *

def main():
    state = State(bird_height=5, bird_velocity=0, pipes=[(10, 10), (32, 5)])
    
    screen = curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    
    try:
        print_state_with_curses(state.render.tolist(), screen)
    except:
        print("failed to print")
        raise
    
    # curses.nocbreak()
    # screen.keypad(False)
    # curses.echo()
    # curses.endwin()

if __name__ == '__main__':
    main()