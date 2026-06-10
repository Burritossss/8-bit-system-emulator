# Imports
from __future__ import annotations
import time
import sys, os
import importlib.util
import sys, os
import importlib.util
# Check if curses is installed, if not, user is most likely running windows and we should let them know that they need windows-curses
try:
    import curses
    from curses import wrapper
except ImportError:
    print("ERR: Curses cannot be found!\n"
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
    print('ERR: Tkinter cannot be found!\n'
    'Please ensure your python environment has Tkinter!')
    sys.exit(1)

#  Import our builtins

# Try to import tkinter for file browsing. Else error
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    print('ERR: Tkinter cannot be found!\n'
    'Please ensure your python environment has Tkinter!')
    sys.exit(1)

#  Import our builtins
from core import CPU, Memory
# Import the API
from core import Canvas
# Import the API
from core import Canvas
# Import settings
from settings import *


def loadModule(source:str, memory:Memory) -> tuple(str, int): # type: ignore

def loadModule(source:str, memory:Memory) -> tuple(str, int): # type: ignore
    '''Dynamically loads a module'''
    if source.endswith('.py'):
        name = os.path.splitext(os.path.basename(source))[0] # Get the name
        spec = importlib.util.spec_from_file_location(name, source) 
        if spec is None or spec.loader is None: 
        name = os.path.splitext(os.path.basename(source))[0] # Get the name
        spec = importlib.util.spec_from_file_location(name, source) 
        if spec is None or spec.loader is None: 
            raise ImportError()
        module = importlib.util.module_from_spec(spec) 

        try:
            spec.loader.exec_module(module) # type: ignore
        except Exception as e:
            return (f"Script Error: {e}", 240)
        
        # Check if the main class is there
        try:
            hardware = getattr(module, "HardwareMod")

            hardware_inst = hardware(memory)

            hardware_inst.setup()
            
            return hardware_inst # type: ignore
        
        except Exception as e:
            return (f'Unable to load Hardware module: {e}', 240)

        module = importlib.util.module_from_spec(spec) 

        try:
            spec.loader.exec_module(module) # type: ignore
        except Exception as e:
            return (f"Script Error: {e}", 240)
        
        # Check if the main class is there
        try:
            hardware = getattr(module, "HardwareMod")

            hardware_inst = hardware(memory)

            hardware_inst.setup()
            
            return hardware_inst # type: ignore
        
        except Exception as e:
            return (f'Unable to load Hardware module: {e}', 240)


def pullMetaData(file:str):
    '''Reads the metadata of a project file'''
    metadata = {
        'NAME':'Unknown',
        'AUTH':'Unknown',
        'VERS':'Unknown',
        'DESC':'Unknown'
    }

    try:
        with open(file, 'r', encoding='utf-8') as f:
            for _ in range(4):
                line = f.readline()
                if not line:
                    break

                line = line.strip().lstrip('#').strip()

                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().upper()
                    value = value.strip()

                    if key in metadata:
                        metadata[key] = value
    
    except Exception:
        pass

    return metadata


def openFilePicker(file:list[tuple[str, str]]):
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
    curses.initscr()
    curses.curs_set(0)
    stdscr.clear()
    stdscr.nodelay(True)

    # Pre-calculate values dealing with the windows
    menu_width:int = int((curses.COLS * 0.75))
    menu_title_x:int = int((menu_width / 2) - (len('Menu')/2))
    controls_width:int = curses.COLS - menu_width
    controls_title_x:int = int((controls_width / 2) - (len('Controls')/2)) # Minus the length of half the controls windows title

    # Create the windows
    menu:curses.window = curses.newwin(curses.LINES-2, menu_width, 1, 0) # Menu window
    controls:curses.window = curses.newwin(curses.LINES-2, curses.COLS - menu_width, 1, menu_width) # controls window
    importmenu:curses.window = curses.newwin(curses.LINES, curses.COLS)
    canvas = Canvas(menu)
    canvas = Canvas(menu)

    # Menu Bar Buttons
    buttons:list[str] = ['[L]oad ROM', '[S]tep', '[R]un', '[I]mport','[Q]uit',]

    # Menu Tabs
    tabs:list[str] = []
    selected_tab = ''

    # Menu Tabs
    tabs:list[str] = []
    selected_tab = ''

    # Message variables
    msg:str = ""
    msgtimer:int = 0

    # Create the Emulator components
    memory:Memory = Memory()
    cpu:CPU = CPU()

    loaded_modules = []

    # Infinite loop
    while True:
        frame_start = time.perf_counter()

        menu.erase() # Clear the module menu

        # CPU handling =============================================================
        if not cpu.paused:
            for _ in range(CYCLESPERFRAME): # Run at 60 fps
                msgtimer, msg = cpu.fetch_decode_execute()

                # Step cpu tick in modules
                for module in loaded_modules:
                    module.cpu_tick()
        
        for module in loaded_modules:
            module.tick(canvas)

                # Step cpu tick in modules
                for module in loaded_modules:
                    module.cpu_tick()
        
        for module in loaded_modules:
            module.tick(canvas)

        # Key Handling =============================================================
        k:int = stdscr.getch() # Get key presses

        if k == ord('s'): # Check if S is pressed, if so step to the next instruction
            if cpu.rom_loaded:
                msgtimer, msg = cpu.fetch_decode_execute()
            else:
                msg = 'ROM is not loaded! Please load a ROM first.'
                msgtimer = 60

        if k == ord('r'): # Check if R is pressed, if so run the CPU
            if cpu.rom_loaded:
                if cpu.paused:
                    cpu.paused = False
                else:
                    cpu.paused = True
            else:
                msg = 'ROM is not loaded! Please load a ROM first.'
                msgtimer = 60
        
        if k == ord('l'): # Check if L is pressed, if so load a ROMWebRTC Control
            # Open the file picker
            file = openFilePicker([("Binary Files", '*.bin')])
            if file:
                try:
                    with open(file, 'rb') as bytes:
                        byte_data = bytes.read()
                        memory.loadROM(byte_data)
                        cpu.reset(memory)
                except Exception as e:
                    msg = f'Failed to load ROM. Reason: {e}'
                    msgtimer = 240
        
        if k == ord('i'): # Check if I is pressed, if so open a file picker and load a .cpl file or a .py file.
            file = openFilePicker([("Component", "*.py *.cpl")])
            if file is not None:
                # Clear the menu and add a border
                importmenu.erase()
                importmenu.border()
                importmenu.noutrefresh()

                # Get metadata of the file:
                metadata = pullMetaData(file)

                importmenu.addstr(1, 1, 'Information:')
                importmenu.addstr(2, 1, f'Name: {metadata['NAME']}')
                importmenu.addstr(3, 1, f'Author: {metadata['AUTH']}')
                importmenu.addstr(4, 1, f'Version: {metadata['VERS']}')
                importmenu.addstr(5, 1, f'Description: {metadata['DESC']}')

                # Check if its a .py file
                if file.endswith('.py'):
                    # If it is, give a warning
                    importmenu.addstr(7,1,'Warning! Loading python hardware modules allows external code execution. Only load .py modules you trust')
                    importmenu.addstr(8,1,'Do you want to continue?')
                    importmenu.addstr(9,1,'Y/n')
                else:
                    # Else don't
                    importmenu.addstr(7,1,'Sorry, currently only Python xmodules are supported at the moment. This is mainly for example purposes')
                    importmenu.addstr(8,1,'y/n')

                curses.doupdate()
                while True:
                    k = importmenu.getch() 
                    if k == ord('Y'):
                        # Load the module
                        hardware = loadModule(file, memory)
                        if isinstance(hardware, tuple):
                            msg = hardware[0]
                            msgtimer = hardware[1]
                            break
                        else:
                            if metadata['NAME'][:4] in tabs:
                                msg = 'Module is already loarded!'
                                msgtimer = 240
                                break
                            loaded_modules.append(hardware)
                            tabs.append(f"{metadata['NAME'][:4]}")
                            selected_tab = f"{metadata['NAME'][:4]}"
                            msg = f"Succesfully loaded module {metadata['NAME']}!"
                            msgtimer = 120
                            break
                    elif k == ord('n'):
                        break
            importmenu.erase()
            importmenu.noutrefresh()

        if k == ord('q'): # Check if Q is pressed, if so exit the Emulator
            memory.close()
            break

        # Drawing ====================================================================
        controls.erase() # Clear the controls screen to prevent the previous things being shown

        # Clear the bottom line
        stdscr.move(curses.LINES - 1, 0)
        stdscr.clrtoeol()
        # Draw the borders of the windows
        menu.border()
        controls.border()
        
        # Menu Bar Drawing
        total_x = 1
        for button in buttons:
            stdscr.addstr(0, total_x, button)
            total_x += len(button)+1
        
        # Tab drawing
        total_x = 1
        for tab in tabs:
            menu.addstr(0, total_x, tab, curses.A_STANDOUT)
            total_x += len(tab)+1

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
            stdscr.addstr(curses.LINES-1, 0, msg)
            msgtimer -= 1
        
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

def debuggerapp():
    from core.instructions import OPCODE_TABLE
    memory = Memory(debugging=True) # Create the memory with Debugging on
    cpu = CPU(True) # Create the CPU with debugging on
    file = ''

    file = openFilePicker([("Binary Files", '*.bin')])

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