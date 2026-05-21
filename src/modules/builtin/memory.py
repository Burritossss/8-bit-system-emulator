'''
Basic memory module settings
'''
from __future__ import annotations

class Memory:
    '''Basic memory class'''
    def __init__(self, size:int=0x10000):
        '''Initilize this memory module'''
        self.memory = bytearray(size)
        #print(f'Memory initilized with size {size/1024} KB')
    
    def write(self, address:int, value:int):
        '''Writes to a value in memory'''
        self.memory[address] = value & 0xFF
        #print(f'Wrote {value & 0xFF} to {address:#4x}')
        #print(self.memory[address])

    def read(self, address:int):
        '''Reads a value in memory'''
        #print(f'Read {self.memory[address & 0xFFFF]:#2x}')
        return self.memory[address & 0xFFFF]

    def loadROM(self, bytes:bytes):
        '''Loads the program ROM'''
        for i, byte in enumerate(bytes):
            self.write(0x9000 + i, byte)
        self.write(0xFFFF, 0x90)