'''
The default CPU class that holds all CPU variables, methods, instructions, and etc.
'''
import memory # Import memory for the basic functions

class Instructions:
    pass

class CPU:
    def __init__(self):
        '''Create the CPU object and create the variables'''
        self.memory:memory.Memory

        self.A:int
        self.X:int
        self.Y:int
        self.PC:int
        self.IR:int
        self.flags:int
    
    def reset(self, memory:memory.Memory):
        '''Resets the CPU'''
        self.memory = memory
        
        # Reset the registers
        self.A = 0
        self.X = 0
        self.Y = 0
        self.PC = (memory.read(0xFFFF) << 8) | memory.read(0xFFFE)
        print(f'PC reset to {hex(self.PC)}')
        self.IR = 0
        self.flags = 0