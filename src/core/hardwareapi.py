'''
File containing all the functions for the hardware API
'''
# Imports
from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Any
from abc import ABC

if TYPE_CHECKING:
    from .memory import Memory
    from curses import window

class hardwareAPI(ABC):
    '''API for writing custom hardware modules'''
    def __init__(self, memory:Memory):
        self.memory = memory

    def setup(self):
        '''Runs when the module is loaded'''
        pass
    
    def tick(self):
        '''Runs every tick of the emulator'''
        pass

    def cpu_tick(self):
        '''Runs every cpu cycle'''
        pass

    def readMemory(self, address:int):
        return self.memory.read(address)
    
class Canvas:
    '''API for writing to the screen'''
    def __init__(self, window:window):
        self.__window = window
    
    def draw_text(self, x:int, y:int, content:Any):
        self.__window.addstr(x, y, content)