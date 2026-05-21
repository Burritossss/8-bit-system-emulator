# Import curses
import curses
from curses import wrapper
# Import tkinter for file browser
import tkinter as tk
from tkinter import filedialog
import time
from modules.builtin import CPU, Memory # Import our builtins

def openFilePicker():
    '''Opens a file picker to let you open a ROM'''
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    rom_path = filedialog.askopenfilename(filetypes=[("Binary Files", '*.bin')])
    root.destroy()
    return rom_path if rom_path else None

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
    menu = curses.newwin(curses.LINES-1, menu_width) # Menu window
    controls = curses.newwin(curses.LINES-1, curses.COLS - menu_width, 0, menu_width) # controls window

    # Setup the titles
    controls.addstr(1, controls_title_x, 'Controls')
    menu.addstr(1, menu_title_x, 'Menu')


    # Menu Bar Buttons
    buttons = ['[L]oad ROM', '[Q]uit', '[S]tep']

    # Create the Emulator components
    memory = Memory()
    cpu = CPU()

    # Infinite loop
    while True:
        # Draw the borders of the windows
        menu.border()
        controls.border()

        # Menu Bar Drawing ==========================================================
        total_x = 1
        for button in buttons:
            stdscr.addstr(0, total_x, button)
            total_x += len(button)+1

        # Controls Drawing ==========================================================
        controls.clear() # Clear the controls screen to prevent the previous things being shown

        controls.addstr(2, 1, f'ROM Loaded: {cpu.rom_loaded}') # If the ROM is loaded
        
        # Registers
        try:    
            controls.addstr(4, 1, f'A: {cpu.a}') # A Register
            controls.addstr(5, 1, f'X: {cpu.x}') # X Register
            controls.addstr(6, 1, f'Y: {cpu.y}') # Y Register
        except AttributeError:
            controls.addstr(4, 1, 'A: N/A')
            controls.addstr(5, 1, 'X: N/A')
            controls.addstr(6, 1, 'Y: N/A')
        
        try: controls.addstr(8, 1, f'PC: {cpu.pc}')
        except AttributeError: controls.addstr(8, 1, 'PC: N/A')

        # Key Handling =============================================================
        k = stdscr.getch() # Get key presses

        if k == ord('s'): # Check if S is pressed, if so, step to the next instruction
            if cpu.rom_loaded:
                cpu.fetch_decode_execute()
            else:
                stdscr.addstr(curses.LINES-1, 0, 'ROM is not loaded! Please load a ROM first.')

        if k == ord('l'): # Check if L is pressed, if so, load a ROM
            # Open the file picker
            file = openFilePicker()
            if file:
                with open(file, 'rb') as bytes:
                    byte_data = bytes.read()
                try:
                    memory.loadROM(byte_data)
                    cpu.reset(memory)
                except Exception as e:
                    stdscr.addstr(curses.LINES-1, 0, f'Failed to load ROM. Reason: {e}')

        if k == ord('q'): # Check if Q is pressed, if so, exit the program
            break

        # Refresh Screen =================================================
        menu.noutrefresh()
        controls.noutrefresh()
        curses.doupdate()

        time.sleep(0.1)


if __name__ == '__main__':
    wrapper(app)