'''
The default CPU class that holds all CPU variables, methods, instructions, and etc.
'''
from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Callable

if TYPE_CHECKING:
    from .memory import Memory

class CPU:
    def __init__(self):
        '''Create the CPU object and create the variables'''
        self.memory:Memory

        self.a:int
        self.x:int
        self.y:int
        self.ir:int
        self.flags:int
        
        self.pc:int
    
    def reset(self, memory:Memory):
        '''Resets the CPU'''
        self.memory = memory

        # Reset the registers
        self.a = 0
        self.x = 0
        self.y = 0
        self.ir = 0
        self.flags = 0

        self.pc = (memory.read(0xFFFF) << 8) | memory.read(0xFFFE)
        print(f'PC reset to {hex(self.pc)}')
    
    def fetch_decode_execute(self, memory:Memory):
        self.pc = (self.pc + 1) & 0xFFFF
        self.ir = memory.read(self.pc)
    