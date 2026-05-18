'''
Basic memory module settings
'''

class Memory:
    '''Basic memory class'''
    def __init__(self, size=0xFFFF):
        '''Initilize this memory module'''
        self.memory = bytearray(size)
        print(f'Memory initilized with size {hex(size)}')
    
    def write(self, address:int, value:int):
        '''Writes to a value in memory'''
        self.memory[address] = value & 0xFF
        print(f'Wrote {value} to {address}')

    def read(self, address:int):
        '''Reads a value in memory'''
        print(f'Read {self.memory[address]}')
        return self.memory[address & 0xFFFF]