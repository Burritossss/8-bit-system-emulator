# Imports
from __future__ import annotations
import time
import sys, os
import importlib.util # Import importlib.util for importing dynamically
import importlib.abc
from typing import Any
# Check if curses is installed, if not, user is most likely running windows and we should let them know that they need windows-curses
try:
    import curses
    from curses import wrapper
except ImportError:
    print("Curses cannot be found!\n"
    "Please either launch with --debug flag or install Curses!")
    print('Possible fix:')
    if sys.platform.startswith("win"):
        print('\tpip install windows-curses')
    else:
        print('\tEnsure Curses is installed in your python environment.')
    sys.exit(1)

# Try to import tkinter for file browsing. Else error
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    print('Tkinter cannot be found!\n'
    'Please ensure your python environment has Tkinter.')
    sys.exit(1)

#  Import our builtins
from core import CPU, Memory
# Import the API
from core import Canvas
# Import settings
from settings import *


def loadModule(source:str, memory:Memory) -> tuple[str, int]|Any:
    '''Dynamically loads a module'''
    if source.endswith('.py'):
        name = os.path.splitext(os.path.basename(source))[0] # Get the name
        spec = importlib.util.spec_from_file_location(name, source) # Create a spec for the library 
        if spec is None or spec.loader is None: 
            raise ImportError()
        module = importlib.util.module_from_spec(spec)  # import the module from the spec

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            return (f"Script Error: {e}", 240)
        
        # Check if the main class is there
        try:
            hardware = getattr(module, "HardwareMod")
            hardware_inst = hardware(memory)
            hardware_inst.setup()

            # Return the harware instance
            return hardware_inst # type: ignore
        
        except Exception as e:
            return (f'Unable to load Hardware module: {e}', 240)


def pullMetaData(file:str) -> dict[str,str]:
    '''Reads the metadata of a project file'''
    # Define the preset metadata to unknown
    metadata = {
        'NAME':'Unknown',
        'AUTH':'Unknown',
        'VERS':'Unknown',
        'DESC':'Unknown'
    }

    try:
        with open(file, 'r', encoding='utf-8') as f: # Open the file
            for _ in range(4): # and read the first four lines
                line = f.readline()
                if not line:
                    break

                line = line.strip().lstrip('#').strip() # Strip out the hashtags 

                if ":" in line: # Check for a colon
                    key, value = line.split(":", 1) # and split the text between the colon into a key and value
                    key = key.strip().upper()
                    value = value.strip()

                    if key in metadata: # Check if the key is correct and in the metadata
                        metadata[key] = value # Set the metadata
    
    except Exception:
        pass # Keep the value of that value of metadata unknown

    return metadata # Return the metadata


def openFilePicker(file:list[tuple[str, str]]) -> str | None:
    '''Opens a file picker to let you open a file'''
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True) # type: ignore
    rom_path = filedialog.askopenfilename(filetypes=file)
    root.destroy()
    return rom_path if rom_path else None

# Application
def app(stdscr:curses.window):
    # ================ Setup =================
    # Initilize curses and the window
    curses.initscr()
    curses.curs_set(0)
    stdscr.clear()
    stdscr.nodelay(True)

    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

    # Pre-calculate values dealing with the windows
    module_menu_width:int = int(curses.COLS * 0.75)
    module_menu_title_x:int = int((module_menu_width / 2) - (len('Modules')/2))
    controls_menu_width:int = curses.COLS - module_menu_width
    controls_menu_title_x:int = int((controls_menu_width / 2) - (len('Controls')/2)) # Minus the length of half the controls windows title

    # Create the windows
    module_menu:curses.window = curses.newwin(curses.LINES-2, module_menu_width, 1, 0) # Module menu window
    controls_menu:curses.window = curses.newwin(curses.LINES-2, curses.COLS - module_menu_width, 1, module_menu_width) # Controls menu window
    import_menu:curses.window = curses.newwin(curses.LINES, curses.COLS) # Import menu window
    canvas:Canvas = Canvas(module_menu)

    # Menu Bar Buttons
    buttons:list[str] = ['[X]', '[L]', '[I]', '[S]', '[R]', ]

    # Menu Tabs
    tabs:list[str] = []
    selected_tab:str =  ""

    # Message variables
    msg:str = ""
    msgtimer:int = 0

    # Create the Emulator components
    memory:Memory = Memory()
    cpu:CPU = CPU()

    loaded_modules:Any = [] # List of modules loaded
    
    unicodetable = {0: '', # Codes of MY version of unicode
                             1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i', 10: 'j', 11: 'k', 12: 'l', 13: 'm', 14: 'n', 15: 'o', 16: 'p', 17: 'q', 18: 'r', 19: 's', 20: 't', 21: 'u', 22: 'v', 23: 'w', 24: 'x', 25: 'y', 26: 'z',
                             27: 'A', 28: 'B', 29: 'C', 30: 'D', 31: 'E', 32: 'F', 33: 'G', 34: 'H', 35: 'I', 36: 'J', 37: 'K', 38: 'L', 39: 'M', 40: 'N', 41: 'O', 42: 'P', 43: 'Q', 44: 'R', 45: 'S', 46: 'T', 47: 'U', 48: 'V', 49: 'W', 50: 'X', 51: 'Y', 52: 'Z',
                             53: '0', 54: '1', 55: '2', 56: '3', 57: '4', 58: '5', 59: '6', 60: '7', 61: '8', 62: '9'}
    
    # Infinite loop
    while True:
        frame_start = time.perf_counter() # Check the start of the frame

        module_menu.erase() # Clear the module menu

        # CPU handling =============================================================
        if not cpu.paused: # Check if the CPU is paused
            for _ in range(CYCLESPERFRAME): # Run at the Cycles per frame to reach target CPU speed
                msgtimer, msg = cpu.fetch_decode_execute() # Fetch, Decode, and execute instructions

                # Step cpu tick in modules
                for module in loaded_modules: # Go through every module
                    try:
                        module.cpu_tick() # Tick the cpu code for the module
                    except Exception as e: # Check if there was an exception, give the error code, and stop the CPU from running
                        msg = f"Module {module} had a CPU tick error: {e}"
                        msgtimer = 480
                        cpu.paused = True
        
        for module in loaded_modules: # Go through every module
            try:
                module.tick(canvas) # Tick the tick function for the module
            except Exception as e:
                msg = f"Module {module} had a ticking error: {e}" # Throw an error if there was an error
                msgtimer = 1

        # Key Handling =============================================================
        k:int = stdscr.getch() # Get key presses
        msg = f'key: {k}'
        msgtimer = 120

        if k != -1:
            if k == curses.KEY_MOUSE:
                _, x, y, _, _ = curses.getmouse()
                if y == 0:
                    if (1 <= x <= 3): # Check if pressing the X button, if so quit
                        memory.close()
                        break

                    if (5 <= x <= 7): # Check if pressing the Load button, if so, load a rom 
                        # Open the file picker
                        file = openFilePicker([("Binary Files", '*.bin')])
                        if file: # Check if the file isn't None
                            try: 
                                with open(file, 'rb') as bytes:
                                    byte_data = bytes.read()
                                    memory.loadROM(byte_data)
                                    cpu.reset(memory)
                            except Exception as e:
                                msg = f'Failed to load ROM. Reason: {e}'
                                msgtimer = 240
                    
                    if (9 <= x <= 11): # Check if pressing the import button, if so import a module
                        file = openFilePicker([("Component", "*.py *.cpl")])
                        if file is not None:
                            # Clear the menu and add a border
                            import_menu.erase()
                            import_menu.border()
                            import_menu.noutrefresh()

                            # Get metadata of the file:
                            metadata = pullMetaData(file)

                            import_menu.addstr(1, 1, 'Information:')
                            import_menu.addstr(2, 1, f'Name: {metadata['NAME']}')
                            import_menu.addstr(3, 1, f'Author: {metadata['AUTH']}')
                            import_menu.addstr(4, 1, f'Version: {metadata['VERS']}')
                            import_menu.addstr(5, 1, f'Description: {metadata['DESC']}')

                            # Check if its a .py file
                            if file.endswith('.py'):
                                # If it is, give a warning
                                import_menu.addstr(7,1,'Warning! Loading python hardware modules allows external code execution. Only load .py modules you trust')
                                import_menu.addstr(8,1,'Do you want to continue?')
                                import_menu.addstr(9,1,'Y/n')
                            else:
                                # Else don't
                                import_menu.addstr(7,1,'Sorry, currently only Python modules are supported at the moment. This is mainly for example purposes')
                                import_menu.addstr(8,1,'y/n')

                            curses.doupdate() # update the screen before checking for user input
                            while True:
                                k = import_menu.getch() # Get user input 
                                if k == ord('Y'): # check if Y was pressed
                                    # Load the module
                                    hardware = loadModule(file, memory)
                                    if isinstance(hardware, tuple): # Error checking
                                        msg = hardware[0]
                                        msgtimer = hardware[1]
                                        break
                                    else:
                                        if metadata['NAME'][:4] in tabs: # Check if module exists
                                            msg = 'Module is already loaded!'
                                            msgtimer = 240
                                            break
                                        loaded_modules.append(hardware) # Load the module
                                        tabs.append(f"{metadata['NAME'][:4]}") # Append the name to the tabs
                                        selected_tab = f"{metadata['NAME'][:4]}" # then set the selected tab to it
                                        msg = f"Succesfully loaded module {metadata['NAME']}!"
                                        msgtimer = 120
                                        break

                                elif k == ord('n'): # Break if n
                                    break
                                
                        import_menu.erase()
                        import_menu.noutrefresh()
                    
                    if (13 <= x <= 15): # Check if pressing S button, if so step to the next instruction
                        if cpu.rom_loaded: # Check if a rom is loaded
                            msgtimer, msg = cpu.fetch_decode_execute()
                        else:
                            msg = 'ROM is not loaded! Please load a ROM first.'
                            msgtimer = 60

                    if (17 <= x <= 19): # Check if pressing R button, if so toggle between running and not running the CPU
                        if cpu.rom_loaded: # Check if the rom is loaded
                            if cpu.paused: # Do a flip flop type check
                                cpu.paused = False
                            else:
                                cpu.paused = True
                        else: 
                            msg = 'ROM is not loaded! Please load a ROM first.'
                            msgtimer = 60

        # Drawing ====================================================================
        controls_menu.erase() # Clear the controls screen to prevent the previous things being shown

        # Clear the bottom line
        stdscr.move(curses.LINES - 1, 0)
        stdscr.clrtoeol()
        # Draw the borders of the windows
        module_menu.border()
        controls_menu.border()
        
        # Menu Bar Drawing
        total_x = 1
        for button in buttons: # Loop for each of the buttons
            stdscr.addstr(0, total_x, button)
            total_x += len(button)+1
        
        # Tab drawing
        total_x = 1
        for tab in tabs: # Loop over each of the tabs
            module_menu.addstr(0, total_x, tab, curses.A_STANDOUT)
            total_x += len(tab)+1

        # Setup the titles
        controls_menu.addstr(1, controls_menu_title_x, 'Controls')
        module_menu.addstr(1, module_menu_title_x, 'Menu')

        controls_menu.addstr(3, 1, f'ROM Loaded: {cpu.rom_loaded}') # If the ROM is loaded
        
        # Registers
        try:    
            controls_menu.addstr(5, 1, f'A: {cpu.a:#04x}') # A Register
            controls_menu.addstr(6, 1, f'X: {cpu.x:#04x}') # X Register
            controls_menu.addstr(7, 1, f'Y: {cpu.y:#04x}') # Y Register
        except AttributeError:
            controls_menu.addstr(5, 1, 'A: N/A')
            controls_menu.addstr(6, 1, 'X: N/A')
            controls_menu.addstr(7, 1, 'Y: "jrsty:' \
            'N/A')

        try: controls_menu.addstr(8, 1, f'PC: {cpu.pc:#06x}') # Program Counter
        except AttributeError: controls_menu.addstr(8, 1, 'PC: N/A')

        # Draw messages
        if msgtimer > 0:
            stdscr.addstr(curses.LINES-1, 0, msg)
            msgtimer -= 1
        
        executiontime = time.perf_counter() - frame_start # Check the difference between the start and end of the frame
        sleep = TARGETDELTATIME - executiontime
        if sleep > 0.001: # Lock to 60 fps
            time.sleep(sleep)
        else:
            time.sleep(0.002)

        # Calculate FPS
        elapsed = time.perf_counter() - frame_start 
        fps = 1.0 / elapsed
        try:
            stdscr.addstr(curses.LINES-1, curses.COLS - len(f'FPS: {fps:.2f}')-2, f'FPS: {fps:.2f}') # Print FPS to the screen
        except:
            pass

        # Refresh Screen =================================================
        module_menu.noutrefresh()
        controls_menu.noutrefresh()
        curses.doupdate()

def debuggerapp(): 
    '''Debugger version for testing things or unable to run the main version. Also useful if modifications use the print command'''
    from core.instructions import OPCODE_TABLE
    memory = Memory(debugging=True) # Create the memory with Debugging on
    cpu = CPU(True) # Create the CPU with debugging on
    file = ''

    file = openFilePicker([("Binary Files", '*.bin')])
    if file:
        try:
            with open(file, 'rb') as bytes:
                print('Reading ROM')
                byte_data = bytes.read()
                print('ROM read, writing')
                memory.loadROM(byte_data)
                cpu.reset(memory)
        except Exception as e:
            quit(f'Failed to load ROM. Reason: {e}')
    else:
        sys.exit(0)
    
    while True:
        cpu.fetch_decode_execute()
        print(f'A: {cpu.a:#04x}, X: {cpu.x:#04x}, Y: {cpu.y:#04x}, PC: {cpu.pc:#06x} INSTRUCTION: {OPCODE_TABLE[cpu.ir].__name__}')
        if input() == 'q':
            break

    memory.close()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print(
        "Usage:"
        "\tpython3 main.py [options]\n"
        "Options:\n"
        "\t--help\t\tDisplays this message\n"
        "\t--debug\t\tSwitches to debugger mode")
        sys.exit()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--debug':
        debuggerapp()
    else:
        wrapper(app)