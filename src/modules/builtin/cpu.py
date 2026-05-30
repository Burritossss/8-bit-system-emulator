'''
The default CPU class that holds all CPU variables, methods, instructions, and etc.
'''
from __future__ import annotations
from typing import TYPE_CHECKING
from .instructions import OPCODE_TABLE

if TYPE_CHECKING:
    from .memory import Memory

class CPU:
    def __init__(self, debugging:bool=False):
        '''Create the CPU object and create the variables'''
        self.memory:Memory

        self.a:int
        self.x:int
        self.y:int
        self.ir:int
        self.flags:int
        self.sp:int
        
        self.pc:int

        self.paused = True # CPU starts paused
        self.rom_loaded = False # CPU starts without a ROM
        self.debugging = debugging # Set debugging mode

        # Define flag masks
        FL_ZERO = 0b00000001
    
    def reset(self, memory:Memory):
        '''Resets the CPU'''
        self.memory = memory

        # Reset the registers
        self.a = 0
        self.x = 0
        self.y = 0
        self.ir = 0
        self.sp = 0xFF
        self.flags = 0

        # Reset the PC
        self.pc = ((memory.read(0xFFFF) << 8) | memory.read(0xFFFE))
        if self.debugging:
            print(f'PC reset to {hex(self.pc)}')
        
        self.rom_loaded = True # ROM has been loaded

    
    def fetch_decode_execute(self) -> tuple[int, str]: #type: ignore
        '''Fetch, decode, and execute an instruction'''
        self.ir = self.memory.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF

        if self.ir in OPCODE_TABLE:
            OPCODE_TABLE[self.ir](self, self.memory)
            return (1, 'Executing...')
        else:
            if self.debugging:
                print(f'ERR: UNKNOWN {self.ir:#02x} @ {self.pc:#04x}')
            else:
                self.paused = True
                return (120, f'ERR: UNKNOWN {self.ir:#02x} @ {self.pc:#04x}')
    