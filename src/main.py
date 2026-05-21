import curses
from curses import wrapper
import time
from modules.builtin import CPU, Memory # Import our builtins

# Application
def app(stdscr:curses.window):
    # ================ Setup =================
    curses.initscr()
    curses.curs_set(0)
    stdscr.clear()
    stdscr.nodelay(True)
    
    # Pre-calculate values dealing with the windows
    menu_width = int((curses.COLS * 0.75))
    menu_title_x = int((menu_width / 2) - (len('Menu')/2))
    controls_width = curses.COLS - menu_width
    controls_title_x = int((controls_width / 2) - (len('Controls')/2)) # Minus the length of half the controls windows title

    # Create the windows for the two sides of the screen
    menu = curses.newwin(curses.LINES-1, menu_width, 1, 0) # Menu window
    controls = curses.newwin(curses.LINES-1, curses.COLS - menu_width, 1, menu_width) # controls window

    # Setup the titles
    controls.addstr(1, controls_title_x, 'Controls')
    menu.addstr(1, menu_title_x, 'Menu')

    menu.border()
    controls.border()

    # Create the Emulator components
    memory = Memory()
    cpu = CPU()

    # Infinite loop
    while True:
        # Show the current state of the processor
        controls.addstr(2, 1, f'ROM Loaded: {cpu.rom_loaded}')
        k = stdscr.getch() # Get key presses

        if k == ord('q'): # Check if Q is pressed, if so, exit the program
            break

        menu.refresh()
        controls.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    wrapper(app)