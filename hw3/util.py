import curses


def print_state_with_curses(state, screen):
    screen.erase()
    screen.scrollok(1)
    for i, row in enumerate(state):
        for j, num in enumerate(row):
            if num == 2:
                screen.addch(i, j, str(num) + '', curses.color_pair(1))
            elif num == 1:
                screen.addch(i, j, str(num) + '', curses.color_pair(2))
            else:
                screen.addch(i, j, str(num))
    screen.refresh()
