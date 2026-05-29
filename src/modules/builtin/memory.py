'''
Basic memory module settings
'''
from __future__ import annotations
import os

class Memory:
    '''Basic memory class'''
    def __init__(self, size:int=0x10000, debugging:bool=False):
        '''Initilize this memory module'''
        self.memory = bytearray(size)
        self.debugging = debugging
        if debugging:
            print(f'Memory initilized with size {size/1024} KB')

        # Banked file setup
        self.bank = 0
        banked_file_path = f'{os.curdir}/storage.bin'

        if not os.path.exists(banked_file_path):
            with open(banked_file_path, 'wb') as f: # Open the storage file
                f.write(bytearray(64 * 1024))

        self.banked_file = open(banked_file_path, 'r+b')
    
    def write(self, address:int, value:int, force:bool=True):
        address &= 0xFFFF # Keeps the address within the 64kb of memory

        '''Writes to a value in memory'''
        if address >= 0x7000 and not force: # Check if trying to write to rom w/o force enabled
            raise PermissionError(f'Unable to write to {address:#06x}. Read Only.')
        
        if address == 0x6000: # Check if writing to bank select
            self.bank = value % 64

        if 0x6001 <= address <= 0x6400: # Check if writing to the storage file
            write_address = (self.bank * 1024) + (address - 0x6001)
            self.banked_file.seek(write_address)
            self.banked_file.write(bytes([value & 0xFF]))
            self.banked_file.flush()
            if self.debugging:
                print(f'Wrote to bank {self.bank}')

        self.memory[address] = value & 0xFF
        
        if self.debugging:
            print(f'Wrote {value:#04x} to {address:#06x}')

    def read(self, address:int):
        '''Reads a value in memory'''
        address &= 0xFFFF # Keeps the address within the 64kb of memory
        if self.debugging:
            print(f'Read {self.memory[address]:#04x}')
        return self.memory[address]

    def loadROM(self, bytes:bytes):
        '''Loads the program ROM'''
        for i, byte in enumerate(bytes):
            self.write(0x7000 + i, byte)
        self.write(0xFFFF, 0x70)
        if self.debugging:
            print('Loaded ROM successfully')
    
    def close(self):
        '''MAKE SURE THIS RUNS TO CLOSE THE FILE OR BAD THINGS HAPPEN'''
        self.banked_file.close()