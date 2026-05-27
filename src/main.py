# Import curses
import curses
from curses import wrapper
# Import tkinter for file browser
import tkinter as tk
from tkinter import filedialog
import time
from modules.builtin import CPU, Memory # Import our builtins
from settings import * # Import settings

def openFilePicker():
    '''Opens a file picker to let you open a ROM'''
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True) # type: ignore
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
    menu = curses.newwin(curses.LINES-2, menu_width, 1, 0) # Menu window
    controls = curses.newwin(curses.LINES-2, curses.COLS - menu_width, 1, menu_width) # controls window

    # Menu Bar Buttons
    buttons = ['[L]oad ROM', '[S]tep', '[R]un', '[Q]uit',]

    # Message variables
    msg:str = ""
    msgtimer:int = 0

    # Create the Emulator components
    memory = Memory()
    cpu = CPU()

    # Infinite loop
    while True:
        frame_start = time.perf_counter()

        # CPU handling =============================================================
        if not cpu.paused:
            for _ in range(CYCLESPERFRAME): # Run at 60 fps
                cpu.fetch_decode_execute()
            msg = "CPU is running"
            msgtimer = 1

        # Key Handling =============================================================
        k = stdscr.getch() # Get key presses

        if k == ord('s'): # Check if S is pressed, if so, step to the next instruction
            if cpu.rom_loaded:
                cpu.fetch_decode_execute()
            else:
                msg = 'ROM is not loaded! Please load a ROM first.'
                msgtimer = 60
        
        if k == ord('r'):
            if cpu.paused and cpu.rom_loaded:
                cpu.paused = False
            else:
                cpu.paused = True
        
        if k == ord('l'): # Check if L is pressed, if so, load a ROM
            # Open the file picker
            file = openFilePicker()
            if file:
                try:
                    with open(file, 'rb') as bytes:
                        byte_data = bytes.read()
                        memory.loadROM(byte_data)
                        cpu.reset(memory)
                except Exception as e:
                    msg = f'Failed to load ROM. Reason: {e}'
                    msgtimer = 240

        if k == ord('q'): # Check if Q is pressed, if so, exit the program
            break
        
        # Drawing ====================================================================
        controls.erase() # Clear the controls screen to prevent the previous things being shown
        menu.erase() # Clear the screen

        stdscr.move(curses.LINES - 1, 0)
        stdscr.clrtoeol()
        
        # Menu Bar Drawing
        total_x = 1
        for button in buttons:
            stdscr.addstr(0, total_x, button)
            total_x += len(button)+1

        # Draw the borders of the windows
        menu.border()
        controls.border()

        # Setup the titles
        controls.addstr(1, controls_title_x, 'Controls')
        menu.addstr(1, menu_title_x, 'Menu')

        controls.addstr(3, 1, f'ROM Loaded: {cpu.rom_loaded}') # If the ROM is loaded
        
        
        # Registers
        try:    
            controls.addstr(5, 1, f'A: {cpu.a:#04x}') # A Register
            controls.addstr(6, 1, f'X: {cpu.x:#04x}') # X Register
            controls.addstr(7, 1, f'Y: {cpu.y:#04x}') # Y Register
        except AttributeError:
            controls.addstr(5, 1, 'A: N/A')
            controls.addstr(6, 1, 'X: N/A')
            controls.addstr(7, 1, 'Y: N/A')
        
        try: controls.addstr(8, 1, f'PC: {cpu.pc:#06x}') # Program Counter
        except AttributeError: controls.addstr(8, 1, 'PC: N/A')

        # Draw messages
        if msgtimer > 0:
            msgtimer -= 1
            stdscr.addstr(curses.LINES-1, 0, msg)
        
        executiontime = time.perf_counter() - frame_start
        sleep = TARGETDELTATIME - executiontime
        if sleep > 0.001:
            time.sleep(sleep)
        else:
            time.sleep(0.002)

        # Calculate FPS
        elapsed = time.perf_counter() - frame_start
        fps = 1.0 / elapsed
        try:
            stdscr.addstr(curses.LINES-1, curses.COLS - len(f'FPS: {fps:.2f}')-2, f'FPS: {fps:.2f}')
        except:
            pass

        # Refresh Screen =================================================
        menu.noutrefresh()
        controls.noutrefresh()
        curses.doupdate()


if __name__ == '__main__':
    wrapper(app)