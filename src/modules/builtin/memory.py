'''
Basic memory module settings
'''
from __future__ import annotations

class Memory:
    '''Basic memory class'''
    def __init__(self, size=0x10000):
        '''Initilize this memory module'''
        self.memory = bytearray(size)
        print(f'Memory initilized with size {size/1024} KB')
    
    def write(self, address:int, value:int):
        '''Writes to a value in memory'''
        self.memory[address] = value & 0xFF
        print(f'Wrote {value} to {address}')

    def read(self, address:int):
        '''Reads a value in memory'''
        print(f'Read {self.memory[address & 0x10000]}')
        return self.memory[address & 0x10000]