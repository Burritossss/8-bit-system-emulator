'''
The default CPU class that holds all CPU variables, methods, instructions, and etc.
'''
from __future__ import annotations
from typing import TYPE_CHECKING
from .instructions import OPCODE_TABLE

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

        self.cycles:int # Counter for cycles

        self.paused = True # CPU starts paused
        self.rom_loaded = False # CPU starts without a ROM
    
    def reset(self, memory:Memory):
        '''Resets the CPU'''
        self.memory = memory

        # Reset the registers
        self.a = 0
        self.x = 0
        self.y = 0
        self.ir = 0
        self.flags = 0

        # Reset the PC
        self.pc = ((memory.read(0xFFFF) << 8) | memory.read(0xFFFE)) - 1
        #print(f'PC reset to {hex(self.pc)}')
        self.rom_loaded = True # ROM has been loaded

        self.cycles = 3
    
    def fetch_decode_execute(self):
        '''Fetch, decode, and execute an instruction'''
        self.pc = (self.pc + 1) & 0xFFFF
        self.ir = self.memory.read(self.pc)

        if self.ir in OPCODE_TABLE:
            self.cycles += OPCODE_TABLE[self.ir](self, self.memory)
        else:
            pass #print(f'ERROR: Instruction {self.ir:#2x} at {self.pc:#4x}')

    